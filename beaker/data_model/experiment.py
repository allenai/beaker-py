from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import Field

from .account import Account
from .base import BaseModel, BasePage, MappedSequence, StrEnum
from .job import Job
from .workspace import WorkspaceRef

__all__ = ["Experiment", "Task", "Tasks", "ExperimentsPage", "ExperimentPatch", "ExperimentSort"]


class Experiment(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    author: Account
    created: datetime
    canceled: Optional[datetime] = None
    canceled_for: Optional[str] = None
    workspace_ref: WorkspaceRef
    jobs: Tuple[Job, ...] = Field(default_factory=tuple)

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def workspace(self) -> WorkspaceRef:
        return self.workspace_ref


class Task(BaseModel):
    id: str
    name: Optional[str] = None
    experiment_id: str
    author: Account
    created: datetime
    schedulable: bool = False
    jobs: Tuple[Job, ...] = Field(default_factory=tuple)
    owner: Optional[Account] = None
    #  replica_rank: Optional[int] = None

    @property
    def replica_rank(self) -> Optional[int]:
        if (
            (job := self.latest_job) is not None
            and job.execution is not None
            and (replica_rank := job.execution.replica_rank) is not None
        ):
            return replica_rank
        return None

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def latest_job(self) -> Optional[Job]:
        if not self.jobs:
            return None
        return sorted(self.jobs, key=lambda job: job.status.created)[-1]


class Tasks(MappedSequence[Task]):
    """
    A sequence of :class:`Task` that also behaves like a mapping of task names to tasks,
    i.e. you can use ``get()`` or ``__getitem__()`` with the name of the task.
    """

    def __init__(self, tasks: List[Task]):
        super().__init__(tasks, {task.name: task for task in tasks if task.name is not None})


class ExperimentsPage(BasePage[Experiment]):
    data: Tuple[Experiment, ...]


class ExperimentPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ExperimentSort(StrEnum):
    created = "created"
    author = "author"
    experiment_name = "name"
    experiment_name_or_description = "nameOrDescription"
