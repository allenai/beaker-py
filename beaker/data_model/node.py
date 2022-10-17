from datetime import datetime
from typing import Optional

from .base import BaseModel

__all__ = ["NodeResources", "Node", "NodeUtilization"]


class NodeResources(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None


class Node(BaseModel):
    id: str
    hostname: str
    created: datetime
    limits: NodeResources
    expiry: Optional[datetime] = None
    cordoned: Optional[datetime] = None
    cordon_reason: Optional[str] = None
    cordon_agent_id: Optional[str] = None
    cluster_id: Optional[str] = None
    account_id: Optional[str] = None


class NodeUtilization(BaseModel):
    id: str
    hostname: str
    limits: NodeResources
    running_jobs: int
    used: NodeResources
    free: NodeResources
    cordoned: bool = False
