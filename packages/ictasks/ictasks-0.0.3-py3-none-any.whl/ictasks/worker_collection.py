import sys
import logging
from pathlib import Path

from icsystemutils.cluster.node import ComputeNode
from .worker import Worker, WorkerHost, CoreRange

logger = logging.getLogger(__name__)


class WorkerCollection:
    def __init__(self, cores_per_node: int = 1, proc_per_node: int = 1) -> None:
        self.cores_per_node = cores_per_node
        self.proc_per_node = proc_per_node
        self.path: Path | None = None
        self.items: list[Worker] = []

    def read(self, path: Path):
        self.path = path
        try:
            with open(path, "r") as f:
                nodes = [ComputeNode(n) for n in f.read().splitlines()]
                self.load(nodes)
        finally:
            logger.error(f"Error opening node file {path}. Exiting.")
            sys.exit(2)

    def load(self, nodes: list[ComputeNode]):
        for idx, node in enumerate(nodes):
            if not self._node_is_registered(node):
                self._add_worker(WorkerHost(idx, node))

    def _add_worker(self, host: WorkerHost):
        cores_per_task = int(self.cores_per_node / self.proc_per_node)
        for proc_id in range(self.proc_per_node):
            worker_id = host.id + proc_id % self.cores_per_node
            core_list = self._get_core_range(proc_id, cores_per_task)
            self.items.append(Worker(worker_id, host, core_list))

    def _get_core_range(self, proc_id: int, cores_per_task: int) -> CoreRange:
        start = proc_id % self.cores_per_node * cores_per_task
        end = start + cores_per_task - 1
        return CoreRange(start, end)

    def _node_is_registered(self, node: ComputeNode) -> bool:
        for worker in self.items:
            if worker.host.node.address == node.address:
                return True
        return False

    def __getitem__(self, arg):
        return self.items[arg]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return self.items.__iter__()
