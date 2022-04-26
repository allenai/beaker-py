from datetime import datetime
from typing import Optional

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
