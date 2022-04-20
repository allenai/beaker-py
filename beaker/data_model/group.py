from datetime import datetime
from typing import Optional

from .account import Account
from .base import BaseModel
from .workspace import WorkspaceRef


class Group(BaseModel):
    id: str
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    name: Optional[str] = None
    full_name: Optional[str] = None
    workspace_ref: Optional[WorkspaceRef] = None
