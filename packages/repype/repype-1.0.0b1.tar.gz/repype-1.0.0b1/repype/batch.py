import glob
import multiprocessing
import multiprocessing.connection
import pathlib
import sys
import traceback

import dill
import repype.pipeline
import repype.config
import repype.status
import repype.task
from repype.typing import (
    Dict,
    List,
    Optional,
    PathLike,
    Type,
)
import yaml
    

class RunContext:
    """
    The pipeline and the hyperparameters used to run a task.

    Arguments:
        task: The task to run.
    """

    task: repype.task.Task
    """
    The task to run.
    """

    pipeline: repype.pipeline.Pipeline
    """
    The pipeline to run the task with. Defaults to :meth:`task.create_pipeline()<repype.task.Task.create_pipeline()>`.
    """

    config: repype.config.Config
    """
    The hyperparameters to run the task with. Defaults to :meth:`task.create_config()<repype.task.Task.create_config()>`.
    """

    def __init__(self, task: repype.task.Task):
        assert task.runnable
        self.task = task
        self.pipeline = task.create_pipeline()
        self.config = task.create_config()


def run_task_process(exit_code: multiprocessing.connection.Connection, args_serialized: bytes) -> None:
    """
    Run a task using specific :class:`RunContext` and :class:`repype.status.Status` objects inside a separate process.

    The exit code of the process is sent to the parent process using the `exit_code` connection.
    This is to bypass some interference between the `exitcode` attribute of ``multiprocessing.Process`` objects and threaded workers in Textual:
    https://github.com/Textualize/textual/discussions/4923
    The exit code is 0 upon successful completion, and 1 indicates failure.

    Arguments:
        exit_code: The connection to send the exit code to.
        args_serialized: The serialized arguments to run the task.
            This should be a tuple of the shape ``(rc, status)``, where ``rc`` is a :class:`RunContext` object
            and ``status`` is a :class:`repype.status.Status` object, serialized using dill.
    """
    rc, status = dill.loads(args_serialized)

    # Run the task and exit the child process
    try:
        rc.task.run(rc.config, pipeline = rc.pipeline, status = status)
        exit_code.send(0)  # Indicate success to the parent process

    # If an exception occurs, update the status and re-raise the exception
    except:
        error = sys.exc_info()[0]
        repype.status.update(
            status = status,
            info = 'error',
            task = str(rc.task.path.resolve()),
            traceback = traceback.format_exc(),
            stage = error.stage.id if isinstance(error, repype.pipeline.StageError) else None,
        )
        exit_code.send(1)  # Indicate a failure to the parent process


class Batch:
    """
    A collection of tasks to run.
    Each task is uniquely identified by its path.

    Arguments:
        task_cls: The class to use for tasks. Defaults to :class:`repype.task.Task`.
    """

    tasks: Dict[pathlib.Path, repype.task.Task]
    """
    A dictionary of tasks, indexed by their path.
    """

    task_cls: Type[repype.task.Task]
    """
    The class to use for tasks.
    """

    task_process: Optional[multiprocessing.Process]
    """
    The process running the current task.
    """

    def __init__(self, task_cls: Type[repype.task.Task] = repype.task.Task):
        self.tasks = dict()
        self.task_cls = task_cls
        self.task_process = None

    def task(self, path: PathLike, spec: Optional[dict] = None) -> Optional[repype.task.Task]:
        """
        Retrieve a task by its path.

        The task is loaded from the task specification if it has not been loaded before.
        Otherwise, the previously loaded task is returned.
        The task specification is either the `spec` argument, or the ``task.yml`` file in the task directory.
        The former is precedencial over the latter.

        The `path` argument is used to later:

        #. Identitfy the task using this method
        #. Establish parential relations, see :attr:`repype.task.Task.parent`
        #. Resolve filepaths, see :meth:`repype.pipeline.Pipeline.resolve`
        """
        path = pathlib.Path(path)
        task = self.tasks.get(path)

        # Using the spec argument overrides the spec file
        if spec is None:
            spec_filepath = path / 'task.yml'

            # If neither the spec argument was given, nor the spec file exists, return the previously loaded task
            if not spec_filepath.is_file():
                return task
            
            # If the spec file exists, load the spec
            with spec_filepath.open('r') as spec_file:
                spec = yaml.safe_load(spec_file)
        
        # Retrieve the parent task and instantiate the requested task
        if task is None:
            parent = self.task(path.parent) if path.parent else None
            task = self.task_cls(path = path, spec = spec, parent = parent)
            assert path not in self.tasks
            self.tasks[path] = task
            return task
        
        # Check whether the task has the right spec
        else:
            assert task.spec == spec, f'{path}: Requested specification {spec} does not match previously loaded specification {task.spec}'
            return task
        
    def load(self, root_path: PathLike) -> None:
        """
        Load all tasks from a directory tree.
        """
        root_path = pathlib.Path(root_path)
        assert root_path.is_dir()
        for path in glob.glob(str(root_path / '**/task.yml'), recursive = True):
            self.task(pathlib.Path(path).parent)

    @property
    def contexts(self) -> List[RunContext]:
        """
        Get a list of run contexts for all tasks.
        """
        return [RunContext(task) for task in self.tasks.values() if task.runnable]
    
    @property
    def pending(self) -> List[RunContext]:
        """
        Get a list of run contexts for all pending tasks.
        """
        return [rc for rc in self.contexts if rc.task.is_pending(rc.pipeline, rc.config)]

    def run(self, contexts: Optional[List[RunContext]] = None, status: Optional[repype.status.Status] = None) -> bool:
        """
        Run all pending tasks (or a subset).

        Each task is run in a separate process using :meth:`run_task_process`.
        This ensures that each task runs with a clean environment, and no memory is leaked in between of tasks.

        Arguments:
            contexts: List of run contexts to run. Defaults to all pending tasks.
            status: The status object to update during task execution. Defaults to a new status object.

        Returns:
            True if all tasks were completed successfully, and False otherwise
        """
        assert self.task_process is None, 'A task is already running'
        try:
            
            contexts = self.pending if contexts is None else contexts
            for rc_idx, rc in enumerate(contexts):
                task_status = status.derive()
    
                repype.status.update(
                    status = task_status,
                    info = 'enter',
                    task = str(rc.task.path.resolve()),
                    step = rc_idx,
                    step_count = len(contexts),
                )

                # Run the task in a separate process
                self.task_pipe = multiprocessing.Pipe(duplex = False)
                self.task_process = multiprocessing.Process(target = run_task_process, args = (self.task_pipe[1], dill.dumps((rc, task_status),),))
                self.task_process.start()

                # Wait for the task process to finish
                self.task_process.join()
                exit_code = self.task_pipe[0].recv()
                if exit_code != 0:
                    repype.status.update(
                        status = status,
                        info = 'interrupted',
                        exit_code = exit_code,
                    )

                    # Interrupt task execution due to an error
                    return False

            # All tasks were completed successfully
            return True
        
        finally:
            self.task_process = None

    def cancel(self) -> None:
        """
        Cancel currently running tasks.
        """
        if self.task_process:

            # Try to terminate the process using SIGTERM (wait at most 1 second)
            self.task_process.terminate()
            self.task_process.join(1)

            # Check whether the process ended, if not, ultimately kill it using SIGKILL
            if self.task_process.exitcode is None:
                self.task_process.kill()
                self.task_process.join()

            # The `run` method is sitll waiting for the exit code, so send a value to unblock it
            self.task_pipe[1].send(2)