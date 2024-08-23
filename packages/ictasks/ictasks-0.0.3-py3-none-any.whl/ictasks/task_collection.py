"""
This module is for a collection of tasks
"""

from pathlib import Path
import sys
import logging
import re

from .task import Task


class TaskCollection:

    """
    This is a collection of tasks which can be 'run' over
    a collection of workers
    """

    def __init__(self, work_dir: Path, group_size: int = 1) -> None:
        self.path: Path | None = None
        self.work_dir = work_dir
        self.group_size = group_size

        self.items: list = []
        self.num_grouped_tasks: int = 0

    def append_workdir(self, line: str) -> str:
        if line[-1] == ";":
            return line + " cd " + str(self.work_dir)
        return line + "; cd " + str(self.work_dir)

    def process_line(self, line: str) -> str:
        if self.has_grouped_tasks():
            return self.append_workdir(line)
        return line

    def extract_paths(self, line: str):
        np = re.search(r"^cd (\w+)", line)
        if np is None:
            np = re.search(r"^pushd (\w+)", line)
        if np is None:
            return ""
        return np.groups()[0]

    def has_grouped_tasks(self) -> bool:
        return self.group_size != 1

    def load(self, content: str):
        template_lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped:
                template_lines.append(self.process_line(stripped))

        lines = [
            template_lines[i].replace("%TASKFARM_TASKNUM%", str(i))
            for i in range(len(template_lines))
        ]

        if self.has_grouped_tasks():
            self.num_grouped_tasks = len(lines)
            num_groups = self.num_grouped_tasks // self.group_size + 1
            gs = self.group_size
            commands = filter(
                None,
                [" && ".join(lines[i * gs : (i + 1) * gs]) for i in range(num_groups)],
            )
            for idx, cmd in enumerate(commands):
                self.items.append(Task(str(idx), cmd))
        else:
            for idx, cmd in enumerate(lines):
                self.items.append(Task(str(idx), cmd, self.extract_paths(cmd)))

    def read(self, path: Path):
        self.path = path
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.load(f.read())
        finally:
            logging.error("Error opening task file %s. Exiting.", path)
            sys.exit(2)

    def __iter__(self):
        return self.items.__iter__()

    def __len__(self):
        return len(self.items)
