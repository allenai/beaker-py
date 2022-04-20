from typing import Optional

from .base import BaseModel


class Account(BaseModel):
    id: str
    name: str
    display_name: str
    institution: Optional[str] = None
