from datetime import datetime
from typing import Optional, Tuple

from .base import BaseModel, StrEnum, field_validator
from .job import Job
from .node import NodeResources, NodeUtilization

__all__ = ["ClusterStatus", "Cluster", "ClusterUtilization", "ClusterSpec", "ClusterPatch"]


class ClusterStatus(StrEnum):
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
    status_message: Optional[str] = None
    aliases: Optional[Tuple[str, ...]] = None
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
    user_restrictions: Optional[Tuple[str, ...]] = None
    allow_preemptible_restriction_exceptions: Optional[bool] = None
    compute_source: Optional[str] = None
    max_job_timeout: Optional[int] = None
    max_session_timeout: Optional[int] = None
    require_preemptible_tasks: Optional[bool] = None

    @field_validator("validated")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v

    @field_validator("node_spec")
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
    running_preemptible_jobs: int
    nodes: Tuple[NodeUtilization, ...]
    jobs: Tuple[Job, ...]

    @property
    def id(self) -> str:
        return self.cluster.id


class ClusterSpec(BaseModel):
    name: str
    capacity: int
    preemptible: bool
    spec: NodeResources


class ClusterPatch(BaseModel):
    capacity: Optional[int] = None
    allow_preemptible_restriction_exceptions: Optional[bool] = None
