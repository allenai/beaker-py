from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pydantic import Field, validator

from .account import Account
from .base import BaseModel, IntEnum, StrEnum
from .experiment_spec import DataMount, EnvVar, ImageSource, Priority, TaskSpec

__all__ = [
    "CurrentJobStatus",
    "CanceledCode",
    "JobStatus",
    "ExecutionResult",
    "JobRequests",
    "JobLimits",
    "JobExecution",
    "JobKind",
    "Job",
    "Jobs",
    "JobStatusUpdate",
    "JobPatch",
    "Session",
]


class CurrentJobStatus(StrEnum):
    """
    The status of a job.
    """

    created = "created"
    scheduled = "scheduled"
    running = "running"
    idle = "idle"
    exited = "exited"
    failed = "failed"
    finalized = "finalized"
    canceled = "canceled"
    preempted = "preempted"


class CanceledCode(IntEnum):
    not_set = 0
    system_preemption = 1
    user_preemption = 2
    idle = 3


class JobStatus(BaseModel):
    created: datetime
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    failed: Optional[datetime] = None
    finalized: Optional[datetime] = None
    canceled: Optional[datetime] = None
    canceled_for: Optional[str] = None
    canceled_code: Optional[CanceledCode] = None
    idle_since: Optional[datetime] = None
    exit_code: Optional[int] = None
    message: Optional[str] = None

    @validator(
        "created", "scheduled", "started", "exited", "failed", "finalized", "canceled", "idle_since"
    )
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v

    @property
    def current(self) -> CurrentJobStatus:
        """
        Get the :class:`CurrentJobStatus`.

        :raises ValueError: If status can't be determined.
        """
        if self.finalized is not None:
            return CurrentJobStatus.finalized
        elif self.failed is not None:
            return CurrentJobStatus.failed
        elif self.exited is not None:
            return CurrentJobStatus.exited
        elif self.canceled is not None:
            if self.canceled_code in {CanceledCode.system_preemption, CanceledCode.user_preemption}:
                return CurrentJobStatus.preempted
            else:
                return CurrentJobStatus.canceled
        elif self.idle_since is not None:
            return CurrentJobStatus.idle
        elif self.started is not None:
            return CurrentJobStatus.running
        elif self.scheduled is not None:
            return CurrentJobStatus.scheduled
        elif self.created is not None:
            return CurrentJobStatus.created
        else:
            raise ValueError(f"Invalid status {self}")


class ExecutionResult(BaseModel):
    beaker: str


class JobRequests(BaseModel):
    gpu_count: Optional[int] = None
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    shared_memory: Optional[str] = None


class JobLimits(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpus: Tuple[str, ...] = Field(default_factory=tuple)


class JobExecution(BaseModel):
    task: str
    experiment: str
    spec: TaskSpec
    result: ExecutionResult
    workspace: Optional[str] = None


class JobKind(StrEnum):
    """
    The kind of job.
    """

    execution = "execution"
    session = "session"


class Session(BaseModel):
    command: Optional[Tuple[str, ...]] = None
    env_vars: Optional[Tuple[EnvVar, ...]] = None
    datasets: Optional[Tuple[DataMount, ...]] = None
    image: Optional[ImageSource] = None
    save_image: bool = False
    ports: Optional[Tuple[int, ...]] = None
    ports_v2: Optional[Tuple[Tuple[int, int], ...]] = None
    priority: Optional[Priority] = None
    work_dir: Optional[str] = None
    identity: Optional[str] = None
    constraints: Optional[Dict[str, List[str]]] = None


class Job(BaseModel):
    """
    A :class:`Job` is an execution of a :class:`Task`.

    .. tip::
        You can check a job's exit code with :data:`job.status.exit_code <JobStatus.exit_code>`.
    """

    id: str
    name: Optional[str] = None
    kind: JobKind
    author: Account
    workspace: str
    cluster: Optional[str]
    status: JobStatus
    execution: Optional[JobExecution] = None
    node: Optional[str] = None
    requests: Optional[JobRequests] = None
    limits: Optional[JobLimits] = None
    session: Optional[Session] = None
    host_networking: bool = False
    port_mappings: Optional[Dict[str, int]] = None

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def is_finalized(self) -> bool:
        return self.status.current == CurrentJobStatus.finalized

    @property
    def is_done(self) -> bool:
        """
        Same as :meth:`is_finalized()`, kept for backwards compatibility.
        """
        return self.status.current == CurrentJobStatus.finalized

    @property
    def was_preempted(self) -> bool:
        return self.status.canceled is not None and self.status.canceled_code in {
            CanceledCode.system_preemption,
            CanceledCode.user_preemption,
        }

    def check(self):
        """
        :raises JobFailedError: If the job failed or was canceled.
        """
        from ..exceptions import JobFailedError

        if self.status.exit_code is not None and self.status.exit_code > 0:
            raise JobFailedError(
                f"Job '{self.id}' exited with non-zero exit code ({self.status.exit_code})",
                job=self,
            )
        elif self.status.canceled is not None:
            raise JobFailedError(f"Job '{self.id}' was canceled", job=self)
        elif self.status.failed is not None:
            raise JobFailedError(f"Job '{self.id}' failed", job=self)


class Jobs(BaseModel):
    data: Optional[Tuple[Job, ...]] = None
    next: Optional[str] = None
    next_cursor: Optional[str] = None


class JobStatusUpdate(BaseModel):
    scheduled: Optional[bool] = None
    started: Optional[bool] = None
    exit_code: Optional[int] = None
    failed: Optional[bool] = None
    finalized: Optional[bool] = None
    canceled: Optional[bool] = None
    canceled_for: Optional[str] = None
    canceled_code: Optional[CanceledCode] = None
    idle: Optional[bool] = None
    message: Optional[str] = None


class JobPatch(BaseModel):
    status: Optional[JobStatusUpdate] = None
    limits: Optional[JobLimits] = None
    priority: Optional[Priority] = None
