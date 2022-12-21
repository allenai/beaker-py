from datetime import datetime
from typing import List, Optional, Tuple

from .account import Account
from .base import BaseModel, BasePage, StrEnum
from .workspace import WorkspaceRef

__all__ = [
    "Group",
    "GroupSpec",
    "GroupParameterType",
    "GroupParameter",
    "GroupPatch",
    "GroupsPage",
    "GroupSort",
]


class Group(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    workspace_ref: Optional[WorkspaceRef] = None
    description: Optional[str] = None

    @property
    def workspace(self) -> Optional[WorkspaceRef]:
        return self.workspace_ref


class GroupSpec(BaseModel):
    workspace: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    experiments: Optional[List[str]] = None


class GroupParameterType(StrEnum):
    metric = "metric"
    env = "env"


class GroupParameter(BaseModel):
    type: GroupParameterType
    name: str


class GroupPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    add_experiments: Optional[List[str]] = None
    remove_experiments: Optional[List[str]] = None
    parameters: Optional[List[GroupParameter]] = None


class GroupsPage(BasePage[Group]):
    data: Tuple[Group, ...]


class GroupSort(StrEnum):
    created = "created"
    modified = "modified"
    author = "author"
    group_name = "name"
    group_name_or_description = "nameOrDescription"
