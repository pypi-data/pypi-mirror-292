"""
An environment in which a set of tasks run
"""

import uuid
import logging

from icsystemutils.cluster.node import ComputeNode

from .scheduler.schedulers.slurm import SlurmJob

logger = logging.getLogger(__name__)


class Environment:
    """
    A base compute environment
    """

    def __init__(self) -> None:
        self.job_id: str | None = None
        self.nodelist: list[ComputeNode] = []


class BasicEnvironment(Environment):
    """
    A basic compute environment with e.g. no job scheduler
    This usually corresponds to running locally
    """

    def __init__(
        self, job_id: str | None = None, nodelist: list[str] | None = None
    ) -> None:
        super().__init__()

        if not job_id:
            self.job_id = str(uuid.uuid4())
        else:
            self.job_id = job_id

        if not nodelist:
            self.nodelist = [ComputeNode("localhost")]
        else:
            self.nodelist = [ComputeNode(a) for a in nodelist]


class SlurmEnvironment(Environment):
    """
    A slurm compute environment
    """

    def __init__(self) -> None:
        super().__init__()
        self.slurm_job = SlurmJob()
        self.nodelist = [ComputeNode(a) for a in self.slurm_job.nodes]

    @staticmethod
    def detect() -> bool:
        return bool(SlurmJob.get_id())


def autodetect_environment() -> Environment:
    if SlurmEnvironment.detect():
        logger.info("Detected we are running in a 'slurm' environment")
        return SlurmEnvironment()

    logger.info("No runtime environment detected - using 'basic' environment")
    return BasicEnvironment()
