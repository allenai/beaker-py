from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from pydantic import Field, validator

from .account import Account
from .base import BaseModel
from .experiment_spec import Priority, TaskSpec


class CurrentJobStatus(str, Enum):
    """
    The status of a job.
    """

    created = "created"
    scheduled = "scheduled"
    running = "running"
    idle = "idle"
    exited = "exited"
    finalized = "finalized"


class JobStatus(BaseModel):
    created: datetime
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    failed: Optional[datetime] = None
    finalized: Optional[datetime] = None
    canceled: Optional[datetime] = None
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
        elif self.exited is not None:
            return CurrentJobStatus.exited
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
    sharedMemory: Optional[str] = None


class JobLimits(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpus: Tuple[str, ...] = Field(default_factory=tuple)


class JobExecution(BaseModel):
    task: str
    experiment: str
    spec: TaskSpec
    result: ExecutionResult


class JobKind(str, Enum):
    """
    The kind of job.
    """

    execution = "execution"
    session = "session"


class Job(BaseModel):
    """
    A :class:`Job` is an execution of a :class:`Task`.
    """

    id: str
    name: Optional[str] = None
    kind: JobKind
    author: Account
    workspace: str
    cluster: str
    status: JobStatus
    execution: Optional[JobExecution] = None
    node: Optional[str] = None
    requests: Optional[JobRequests] = None
    limits: Optional[JobLimits] = None

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def is_finalized(self) -> bool:
        return self.status.current == CurrentJobStatus.finalized


class Jobs(BaseModel):
    data: Optional[Tuple[Job, ...]] = None
    next: Optional[str] = None


class CanceledCode(int, Enum):
    not_set = 0
    system_preemption = 1
    user_preemption = 2
    idle = 3


class JobStatusUpdate(BaseModel):
    scheduled: Optional[bool] = None
    started: Optional[bool] = None
    exit_code: Optional[int] = None
    failed: Optional[bool] = None
    finalized: Optional[bool] = None
    canceled: Optional[bool] = None
    canceled_for: Optional[CanceledCode] = None
    idle: Optional[bool] = None
    message: Optional[str] = None


class JobPatch(BaseModel):
    status: Optional[JobStatusUpdate] = None
    limits: Optional[JobLimits] = None
    priority: Optional[Priority] = None
