from icsystemutils.cluster.node import ComputeNode


class CoreRange:
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"


class WorkerHost:
    def __init__(self, id: int, node: ComputeNode) -> None:
        self.id = id
        self.node = node


class Worker:
    def __init__(self, id, host: WorkerHost, cores: CoreRange) -> None:
        self.id = id
        self.host = host
        self.cores = cores

    def get_host_address(self) -> str:
        return self.host.node.address
