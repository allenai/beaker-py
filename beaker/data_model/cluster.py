from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from pydantic import validator

from .base import BaseModel
from .node import NodeResources, NodeUtilization


class ClusterStatus(str, Enum):
    """
    Current status of a cluster.
    """

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
    status: ClusterStatus
    node_spec: Optional[NodeResources] = None
    """
    The requested node configuration.
    """
    node_shape: Optional[NodeResources] = None
    """
    The actual node configuration.
    """
    node_cost: Optional[str] = None
    validated: Optional[datetime] = None

    @validator("validated")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v

    @validator("node_spec")
    def _validate_node_spec(cls, v: Optional[NodeResources]) -> Optional[NodeResources]:
        if v is not None and not v.to_json():
            return None
        return v

    @property
    def is_cloud(self) -> bool:
        """
        Returns ``True`` is the cluster is a cloud cluster, otherwise ``False``.
        """
        return self.node_shape is not None and self.node_spec is not None

    @property
    def is_active(self) -> bool:
        """
        Returns ``True`` if the cluster is ready to be used.
        """
        return not self.is_cloud or self.status == ClusterStatus.active


class ClusterUtilization(BaseModel):
    cluster: Cluster
    running_jobs: int
    queued_jobs: int
    nodes: Tuple[NodeUtilization, ...]

    @property
    def id(self) -> str:
        return self.cluster.id


class ClusterSpec(BaseModel):
    name: str
    capacity: int
    preemptible: bool
    spec: NodeResources


class ClusterPatch(BaseModel):
    capacity: int
