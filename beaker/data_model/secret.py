from datetime import datetime

from .base import BaseModel


class Secret(BaseModel):
    name: str
    created: datetime
    updated: datetime
