"""
This module describes a task, i.e. a small unit of work
"""

import json


class Task:

    """
    A task is a small unit of work
    """

    def __init__(
        self, task_id: str, launch_cmd: str, extra_paths: list | None = None
    ) -> None:
        self.task_id = task_id
        self.launch_cmd = launch_cmd
        if extra_paths:
            self.extra_paths = extra_paths
        else:
            self.extra_paths = []

    def serialize(self) -> dict:
        return {
            "id": self.task_id,
            "launch_cmd": self.launch_cmd,
            "extra_paths": self.extra_paths,
        }

    def __str__(self):
        return json.dumps(self.serialize())
