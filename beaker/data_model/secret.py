from datetime import datetime
from typing import Optional

from .base import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    name: str
    created: datetime
    updated: datetime
    author_id: Optional[str] = None
