from datetime import datetime
from enum import Enum
from typing import List, Optional

from .account import Account
from .base import BaseModel
from .workspace import WorkspaceRef


class Group(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    workspace_ref: Optional[WorkspaceRef] = None

    @property
    def workspace(self) -> Optional[WorkspaceRef]:
        return self.workspace_ref


class GroupSpec(BaseModel):
    workspace: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    experiments: Optional[List[str]] = None


class GroupParameterType(str, Enum):
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
