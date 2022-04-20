from datetime import datetime
from typing import Dict, List, Optional

from .account import Account
from .base import BaseModel


class WorkspaceSize(BaseModel):
    datasets: int
    experiments: int
    groups: int
    images: int


class Workspace(BaseModel):
    id: str
    name: str
    full_name: str
    size: WorkspaceSize
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    archived: bool = False


class WorkspaceRef(BaseModel):
    id: str
    name: str
    full_name: str


class WorkspacePage(BaseModel):
    data: List[Workspace]
    next_cursor: Optional[str] = None


class WorkspacePermissions(BaseModel):
    requester_auth: str
    public: bool
    authorizations: Dict[str, str]
    """
    A dictionary of account IDs to authorizations.
    """
