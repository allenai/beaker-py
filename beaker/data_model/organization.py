from datetime import datetime
from enum import Enum

from .account import Account
from .base import BaseModel


class Organization(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    display_name: str


class OrganizationRole(str, Enum):
    admin = "admin"
    member = "member"


class OrganizationMember(BaseModel):
    role: OrganizationRole
    organization: Organization
    user: Account
