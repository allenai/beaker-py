from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .account import Account
from .base import BaseModel
from .job import Job
from .workspace import WorkspaceRef


class Experiment(BaseModel):
    id: str
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    name: Optional[str] = None
    full_name: Optional[str] = None
    jobs: List[Job] = Field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id


class Task(BaseModel):
    id: str
    experiment_id: str
    owner: Account
    author: Account
    created: datetime
    name: Optional[str] = None
    schedulable: bool = False
    jobs: List[Job] = Field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def latest_job(self) -> Optional[Job]:
        if not self.jobs:
            return None
        return sorted(self.jobs, key=lambda job: job.status.created)[-1]


class ExperimentsPage(BaseModel):
    data: List[Experiment]
    next_cursor: Optional[str] = None
