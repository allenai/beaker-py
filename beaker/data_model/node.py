from datetime import datetime
from typing import Optional

from .base import BaseModel


class NodeSpec(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None


class NodeShape(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None


class Node(BaseModel):
    id: str
    hostname: str
    created: datetime
    expiry: datetime
    limits: NodeSpec


class NodeSpecUtil(BaseModel):
    cpu_count: Optional[float] = None
    gpu_count: Optional[int] = None


class NodeUtilization(BaseModel):
    id: str
    hostname: str
    limits: NodeSpec
    running_jobs: int
    used: NodeSpecUtil
    free: NodeSpecUtil
