from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

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
    description: Optional[str] = None
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
    data: Tuple[Workspace, ...]
    next_cursor: Optional[str] = None


class WorkspaceSpec(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    public: bool = False
    org: Optional[str] = None


class WorkspaceTransferSpec(BaseModel):
    ids: List[str]


class Permission(str, Enum):
    """
    Workspace permission levels.
    """

    no_permission = "none"
    read = "read"
    write = "write"
    full_control = "all"


class WorkspacePermissions(BaseModel):
    requester_auth: str
    public: bool
    authorizations: Dict[str, Permission]
    """
    A dictionary of account IDs to authorizations.
    """


class WorkspacePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    archive: Optional[bool] = None


class WorkspacePermissionsPatch(BaseModel):
    public: Optional[bool] = None
    authorizations: Optional[Dict[str, Permission]] = None
