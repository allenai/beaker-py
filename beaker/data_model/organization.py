from datetime import datetime
from enum import Enum
from typing import Optional

from .account import Account
from .base import BaseModel

__all__ = ["Organization", "OrganizationRole", "OrganizationMember"]


class Organization(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    display_name: str
    pronouns: Optional[str] = None


class OrganizationRole(str, Enum):
    admin = "admin"
    member = "member"


class OrganizationMember(BaseModel):
    role: OrganizationRole
    organization: Organization
    user: Account
