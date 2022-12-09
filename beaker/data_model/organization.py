from datetime import datetime
from typing import Optional

from .account import Account
from .base import BaseModel, StrEnum

__all__ = ["Organization", "OrganizationRole", "OrganizationMember"]


class Organization(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    display_name: str
    pronouns: Optional[str] = None


class OrganizationRole(StrEnum):
    admin = "admin"
    member = "member"


class OrganizationMember(BaseModel):
    role: OrganizationRole
    organization: Organization
    user: Account
