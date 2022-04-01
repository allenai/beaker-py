from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as _BaseModel
from pydantic import Field


class BaseModel(_BaseModel):
    def __getitem__(self, key):
        try:
            return self.dict()[key]
        except KeyError:
            if not key.islower():
                snake_case_key = ""
                for c in key:
                    if c.isupper():
                        snake_case_key += "_"
                    snake_case_key += c.lower()
                try:
                    return self.dict()[snake_case_key]
                except KeyError:
                    pass
            raise


class WorkspaceSize(BaseModel):
    datasets: int
    experiments: int
    groups: int
    images: int


class Account(BaseModel):
    id: str
    name: str
    display_name: str = Field(alias="displayName")


class Workspace(BaseModel):
    id: str
    name: str
    size: WorkspaceSize
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    archived: bool = False
    full_name: str = Field(alias="fullName")


class WorkspaceRef(BaseModel):
    id: str
    name: str
    full_name: str = Field(alias="fullName")


class ExecutionState(BaseModel):
    created: Optional[datetime] = None
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    finalized: Optional[datetime] = None
    exit_code: Optional[int] = Field(alias="exitCode")


class JobStatus(BaseModel):
    created: Optional[datetime] = None
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    finalized: Optional[datetime] = None
    exit_code: Optional[int] = Field(alias="exitCode")


class ExecutionResult(BaseModel):
    beaker: str


class Execution(BaseModel):
    id: str
    task: str
    experiment: str
    workspace: str
    author: Account
    node: str
    spec: Dict[str, Any]
    result: ExecutionResult
    state: ExecutionState
    limits: Dict[str, Any]
    priority: str = "normal"


class JobRequests(BaseModel):
    gpu_count: Optional[int] = Field(alias="gpuCount")
    cpu_count: Optional[float] = Field(alias="cpuCount")
    memory: Optional[str] = None
    sharedMemory: Optional[str] = None


class JobLimits(BaseModel):
    cpu_count: Optional[float] = Field(alias="cpuCount")
    memory: Optional[str] = None
    gpus: List[str] = Field(default_factory=list)


class JobExecution(BaseModel):
    task: str
    experiment: str
    workspace: str
    spec: Dict[str, Any]
    result: ExecutionResult


class Job(BaseModel):
    id: str
    kind: str
    name: str
    author: Account
    workspace: str
    cluster: str
    node: str
    status: JobStatus
    requests: JobRequests
    limits: JobLimits
    execution: JobExecution


class Experiment(BaseModel):
    id: str
    name: str
    owner: Account
    author: Account
    created: datetime
    executions: List[Execution] = Field(default_factory=list)
    jobs: List[Job] = Field(default_factory=list)
    workspace_ref: WorkspaceRef = Field(alias="workspaceRef")
    full_name: str = Field(alias="fullName")
