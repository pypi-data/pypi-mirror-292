"""
This module has the context a task is run in
"""

import os
from pathlib import Path
from subprocess import Popen

from .stopping_condition import StoppingCondition
from .worker import Worker
from .task import Task


class TaskContext:

    """
    The context a task is run in
    """

    def __init__(
        self,
        work_dir: Path,
        launch_wrapper,
        worker: Worker,
        task: Task,
        cores_per_task: int,
        job_id: str,
    ) -> None:
        self.work_dir = work_dir
        self.launch_wrapper = launch_wrapper
        self.worker = worker
        self.task = task
        self.cores_per_task = cores_per_task
        self.job_id = job_id
        self.full_cmd = ""

        task_label = f"{self.worker.host}-id{self.worker.id}-{self.job_id}"
        task_file_name = f"task-{task_label}.{self.task.task_id}"
        self.task_file_path = self.work_dir / Path(task_file_name)

        self.stopfile = None
        self.stopfile_magic = ""
        self.stopping_condition = StoppingCondition(
            self.task_file_path, self.stopfile, self.stopfile_magic
        )

        self.pid = None
        self.popen_ctx = None

    def poll(self):
        return self.popen_ctx.poll()

    def get_path(self) -> Path:
        if str(self.task_file_path)[-1] != "/":
            return Path(str(self.task_file_path) + "/")
        return self.task_file_path
    def check_magic(self) -> bool:
        with open(self.get_stop_path(), "r", encoding="utf-8") as f:
            for line in f:
                if self.stopping_condition.stopmagic in line:
                    return True
        return False

    def get_stop_path(self):
        return self.get_path() + self.stopfile

    def check_user_exit(self):
        self.stopping_condition.eval()


class TaskLauncher:

    """
    This class is responsible for launching tasks
    """

    def __init__(self) -> None:
        self.launcher_type = ""
        self.runtime_env = ""
        exclude_params = ["PROFILEREAD", "BASH_FUNC_module()"]
        for param in os.environ:
            if param not in exclude_params:
                export_cmd = f"export {param}='{os.environ[param]}'; "
                self.runtime_env = self.runtime_env + export_cmd

    def write_launch_file(self, task_ctx: TaskContext):
        task_cmd = task_ctx.task.launch_cmd
        wrapped_cmd = f"{self.runtime_env} cd {os.getcwd()} && {task_cmd}"
        with open(task_ctx.task_file_path, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n")
            f.write(wrapped_cmd)
        os.chmod(task_ctx.task_file_path, 0o0755)

    def launch(self, task_ctx: TaskContext):
        self.write_launch_file(task_ctx)

        if self.launcher_type == "basic":
            args: list[str] = [str(task_ctx.task_file_path)]
        else:
            args = [
                task_ctx.launch_wrapper,
                "-env",
                "I_MPI_PIN_PROCESSOR_LIST",
                str(task_ctx.worker.cores),
                "-n",
                str(task_ctx.cores_per_task),
                "-host",
                task_ctx.worker.get_host_address(),
                str(task_ctx.task_file_path),
            ]

        task_ctx.full_cmd = ""
        for arg in args:
            task_ctx.full_cmd += arg + " "

        task_ctx.popen_ctx = Popen(args)  # type: ignore
        task_ctx.pid = task_ctx.popen_ctx.pid  # type: ignore
        return task_ctx
