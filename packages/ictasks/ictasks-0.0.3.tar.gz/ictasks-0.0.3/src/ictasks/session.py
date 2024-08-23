"""
This module is for a single batch job or session
"""

import os
import time
import logging
from pathlib import Path

from .settings import TaskfarmSettings
from .environment import Environment
from .worker_collection import WorkerCollection
from .task_collection import TaskCollection

from .task_context import TaskContext, TaskLauncher
from .utils.queue import Queue

logger = logging.getLogger(__name__)


class Session:
    """This class represents a single batch job or session

    Attributes:
        job_id (str): Idenitifier for the job or session
        nodelist (:obj:`list`): List of compute nodes available to run on
        tasks_path (:obj:`Path`): Path to a list of tasks to run
    """

    def __init__(
        self,
        workdir: Path,
        environment: Environment,
        taskfile_path: Path | None = None,
    ) -> None:

        self.work_dir = workdir
        self.environment = environment

        self.tasks_path = taskfile_path
        self.tasklist = None
        self.tasks = TaskCollection(self.work_dir)

        self.settings = TaskfarmSettings()
        self.launcher = TaskLauncher()
        self.workers = WorkerCollection()

        self.worker_queue = Queue()
        self.running_tasks: dict = {}
        self.is_intialized = False

    def run(self):
        """
        Run the session by iterating over all
        tasks an assigning them to waiting workers.
        """
        self._init()
        self._log_launch_info()

        for task in self.tasks:
            if self.worker_queue.available():
                self._launch(task)
            else:
                worker_id = self._wait_on_task()
                self.worker_queue.push(worker_id)

        while self.running_tasks:
            self._wait_on_task()
        logger.info("All tasks completed.")

    def _init(self):

        """
        Initializing workers and task list
        """
        if self.is_intialized:
            return

        self._init_workers()
        self._init_tasks()

        self.is_intialized = True

    def _init_workers(self):
        self.workers.cores_per_node = self.settings.get_cores_per_node()
        self.workers.proc_per_node = self.settings.processes_per_node
        self.workers.load(self.environment.nodelist)
        for worker in self.workers:
            self.worker_queue.push(worker.id)

    def _init_tasks(self):
        self.tasks.group_size = self.settings.get("group_size")
        if self.tasklist:
            self.tasks.load(self.tasklist)
        elif self.tasks_path:
            self.tasks.read(self.tasks_path)

    def _log_launch_info(self):
        num_workers = len(self.workers)
        num_tasks = len(self.tasks)

        ppn = self.settings.processes_per_node
        logger.info("Session started with %d workers (%d per node).", num_workers, ppn)
        if self.tasks.has_grouped_tasks():
            grouped_tasks = self.tasks.num_grouped_tasks
            logger.info(
                "Session has %d tasks, grouped as %d metatasks.",
                num_tasks,
                grouped_tasks,
            )
        else:
            logger.info("Session has %d tasks.", num_tasks)

        if num_tasks % num_workers != 0:
            logger.warning(
                "Input should be multiple of %d tasks for %d workers.",
                num_workers,
                num_workers,
            )
        if num_tasks / num_workers > 20:
            msg = f"""There are {num_tasks} tasks for {num_workers} workers.
                This tool is not ideal for high-throughput workloads.
                Running many tasks of a very short duration is inefficient.
                You can aggregate tasks using export TASKFARM_GROUP=xxx
                with xxx how many consecutive tasks to group in a metatask"""
            logger.warning(msg)

    def _launch(self, task):
        worker = self.workers[self.worker_queue.pop()]

        task_ctx = TaskContext(
            self.work_dir,
            self.settings.get("launcher"),
            worker,
            task,
            self.settings.cores_per_task,
            self.environment.job_id,
        )
        task_ctx = self.launcher.launch(task_ctx)

        self.running_tasks[task_ctx.pid] = task_ctx

    def _wait_on_task(self):
        finished = {}
        while True:
            for pid, task_ctx in self.running_tasks.items():
                if task_ctx.poll() is not None:
                    finished[pid] = {"status": task_ctx.poll()}
                task_ctx.check_user_exit()

            if len(finished) > 0:
                first_pid = list(finished.keys())[0]
                should_exit = signal = finished[first_pid]["status"]
                break
            time.sleep(self.settings.get("sleep"))

        worker_id = self.running_tasks[first_pid].worker.id
        if should_exit != 0:
            task_cmd = self.running_tasks[first_pid].task.launch_cmd
            logger.error("'%s' killed by sig %d", task_cmd, signal)

        if not self.settings.get("keep"):
            os.unlink(self.running_tasks[first_pid].task_file_path)
            del self.running_tasks[first_pid]
        return worker_id
