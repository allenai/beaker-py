from datetime import datetime

from .base import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    name: str
    created: datetime
    updated: datetime
