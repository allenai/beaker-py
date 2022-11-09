from typing import Optional

from .base import BaseModel

__all__ = ["Account"]


class Account(BaseModel):
    id: str
    name: str
    display_name: str
    institution: Optional[str] = None
    pronouns: Optional[str] = None
    email: Optional[str] = None
