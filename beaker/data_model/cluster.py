from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import validator

from .base import BaseModel
from .node import NodeShape, NodeSpec, NodeUtilization


class ClusterStatus(str, Enum):
    pending = "pending"
    active = "active"
    terminated = "terminated"
    failed = "failed"


class Cluster(BaseModel):
    id: str
    name: str
    full_name: str
    created: datetime
    autoscale: bool
    capacity: int
    preemptible: bool
    status: str
    node_spec: NodeSpec
    node_shape: Optional[NodeShape] = None
    nodeCost: Optional[str] = None
    validated: Optional[datetime] = None

    @validator("validated")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class ClusterUtilization(BaseModel):
    id: str
    running_jobs: int
    queued_jobs: int
    nodes: List[NodeUtilization]
