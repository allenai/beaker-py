from datetime import datetime
from typing import Optional, Tuple

from pydantic import Field

from .account import Account
from .base import BaseModel
from .job import Job
from .workspace import WorkspaceRef


class Experiment(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    jobs: Tuple[Job, ...] = Field(default_factory=tuple)

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id


class Task(BaseModel):
    id: str
    name: Optional[str] = None
    experiment_id: str
    owner: Account
    author: Account
    created: datetime
    schedulable: bool = False
    jobs: Tuple[Job, ...] = Field(default_factory=tuple)

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def latest_job(self) -> Optional[Job]:
        if not self.jobs:
            return None
        return sorted(self.jobs, key=lambda job: job.status.created)[-1]


class ExperimentsPage(BaseModel):
    data: Tuple[Experiment, ...]
    next_cursor: Optional[str] = None


class ExperimentPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
