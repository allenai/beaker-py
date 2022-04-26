from datetime import datetime
from typing import Optional

from .base import BaseModel


class NodeResources(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None


class Node(BaseModel):
    id: str
    hostname: str
    created: datetime
    expiry: datetime
    limits: NodeResources


class NodeUtilization(BaseModel):
    id: str
    hostname: str
    limits: NodeResources
    running_jobs: int
    used: NodeResources
    free: NodeResources
