from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ORDER_UNSPECIFIED: _ClassVar[SortOrder]
    SORT_ORDER_DESCENDING: _ClassVar[SortOrder]
    SORT_ORDER_ASCENDING: _ClassVar[SortOrder]

class AuthRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTH_ROLE_UNSPECIFIED: _ClassVar[AuthRole]
    AUTH_ROLE_DEACTIVATED: _ClassVar[AuthRole]
    AUTH_ROLE_SCIENTIST: _ClassVar[AuthRole]
    AUTH_ROLE_SYSTEM: _ClassVar[AuthRole]
    AUTH_ROLE_ADMIN: _ClassVar[AuthRole]

class GpuType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GPU_TYPE_UNSPECIFIED: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_H100: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_A100_80GB: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_A100_40GB: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_L4: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_RTX_A5000: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_RTX_A6000: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_RTX_8000: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_T4: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_P100: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_P4: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_V100: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_L40: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_L40S: _ClassVar[GpuType]
    GPU_TYPE_NVIDIA_B200: _ClassVar[GpuType]

class CloudClusterStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLOUD_CLUSTER_STATUS_UNSPECIFIED: _ClassVar[CloudClusterStatus]
    CLOUD_CLUSTER_STATUS_PENDING: _ClassVar[CloudClusterStatus]
    CLOUD_CLUSTER_STATUS_ACTIVE: _ClassVar[CloudClusterStatus]
    CLOUD_CLUSTER_STATUS_FAILED: _ClassVar[CloudClusterStatus]
    CLOUD_CLUSTER_STATUS_TERMINATED: _ClassVar[CloudClusterStatus]

class ClusterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLUSTER_TYPE_UNSPECIFIED: _ClassVar[ClusterType]
    CLUSTER_TYPE_ON_PREMISE: _ClassVar[ClusterType]
    CLUSTER_TYPE_CLOUD: _ClassVar[ClusterType]

class ClusterSchedulingPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLUSTER_SCHEDULING_POLICY_UNSPECIFIED: _ClassVar[ClusterSchedulingPolicy]
    CLUSTER_SCHEDULING_POLICY_EAGER: _ClassVar[ClusterSchedulingPolicy]
    CLUSTER_SCHEDULING_POLICY_STRICT_PRIORITY_BACKFILL_PREEMPTIBLE_ONLY: _ClassVar[ClusterSchedulingPolicy]
    CLUSTER_SCHEDULING_POLICY_STRICT_PRIORITY_BACKFILL_ALL: _ClassVar[ClusterSchedulingPolicy]

class JobKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_KIND_UNSPECIFIED: _ClassVar[JobKind]
    JOB_KIND_BATCH: _ClassVar[JobKind]
    JOB_KIND_SESSION: _ClassVar[JobKind]

class WorkloadStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[WorkloadStatus]
    STATUS_SUBMITTED: _ClassVar[WorkloadStatus]
    STATUS_QUEUED: _ClassVar[WorkloadStatus]
    STATUS_INITIALIZING: _ClassVar[WorkloadStatus]
    STATUS_RUNNING: _ClassVar[WorkloadStatus]
    STATUS_STOPPING: _ClassVar[WorkloadStatus]
    STATUS_UPLOADING_RESULTS: _ClassVar[WorkloadStatus]
    STATUS_CANCELED: _ClassVar[WorkloadStatus]
    STATUS_SUCCEEDED: _ClassVar[WorkloadStatus]
    STATUS_FAILED: _ClassVar[WorkloadStatus]
    STATUS_READY_TO_START: _ClassVar[WorkloadStatus]

class CancelationCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CANCELATION_CODE_UNSPECIFIED: _ClassVar[CancelationCode]
    CANCELATION_CODE_SYSTEM_PREEMPTION: _ClassVar[CancelationCode]
    CANCELATION_CODE_USER_PREEMPTION: _ClassVar[CancelationCode]
    CANCELATION_CODE_IDLE: _ClassVar[CancelationCode]
    CANCELATION_CODE_MANUAL: _ClassVar[CancelationCode]
    CANCELATION_CODE_TIMEOUT: _ClassVar[CancelationCode]
    CANCELATION_CODE_NODE_UNAVAILABLE: _ClassVar[CancelationCode]
    CANCELATION_CODE_IMPOSSIBLE_TO_SCHEDULE: _ClassVar[CancelationCode]
    CANCELATION_CODE_SIBLING_TASK_FAILED: _ClassVar[CancelationCode]
    CANCELATION_CODE_SIBLING_TASK_PREEMPTION: _ClassVar[CancelationCode]
    CANCELATION_CODE_HEALTHCHECK_FAILED: _ClassVar[CancelationCode]
    CANCELATION_CODE_SIBLING_TASK_RETRY: _ClassVar[CancelationCode]

class JobPlacementConstraintType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_PLACEMENT_CONSTRAINT_TYPE_UNSPECIFIED: _ClassVar[JobPlacementConstraintType]
    JOB_PLACEMENT_CONSTRAINT_TYPE_CLUSTER: _ClassVar[JobPlacementConstraintType]
    JOB_PLACEMENT_CONSTRAINT_TYPE_HOSTNAME: _ClassVar[JobPlacementConstraintType]

class JobPriority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_PRIORITY_UNSPECIFIED: _ClassVar[JobPriority]
    JOB_PRIORITY_LOW: _ClassVar[JobPriority]
    JOB_PRIORITY_NORMAL: _ClassVar[JobPriority]
    JOB_PRIORITY_HIGH: _ClassVar[JobPriority]
    JOB_PRIORITY_URGENT: _ClassVar[JobPriority]

class WorkloadType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKLOAD_TYPE_UNSPECIFIED: _ClassVar[WorkloadType]
    WORKLOAD_TYPE_EXPERIMENT: _ClassVar[WorkloadType]
    WORKLOAD_TYPE_ENVIRONMENT: _ClassVar[WorkloadType]
SORT_ORDER_UNSPECIFIED: SortOrder
SORT_ORDER_DESCENDING: SortOrder
SORT_ORDER_ASCENDING: SortOrder
AUTH_ROLE_UNSPECIFIED: AuthRole
AUTH_ROLE_DEACTIVATED: AuthRole
AUTH_ROLE_SCIENTIST: AuthRole
AUTH_ROLE_SYSTEM: AuthRole
AUTH_ROLE_ADMIN: AuthRole
GPU_TYPE_UNSPECIFIED: GpuType
GPU_TYPE_NVIDIA_H100: GpuType
GPU_TYPE_NVIDIA_A100_80GB: GpuType
GPU_TYPE_NVIDIA_A100_40GB: GpuType
GPU_TYPE_NVIDIA_L4: GpuType
GPU_TYPE_NVIDIA_RTX_A5000: GpuType
GPU_TYPE_NVIDIA_RTX_A6000: GpuType
GPU_TYPE_NVIDIA_RTX_8000: GpuType
GPU_TYPE_NVIDIA_T4: GpuType
GPU_TYPE_NVIDIA_P100: GpuType
GPU_TYPE_NVIDIA_P4: GpuType
GPU_TYPE_NVIDIA_V100: GpuType
GPU_TYPE_NVIDIA_L40: GpuType
GPU_TYPE_NVIDIA_L40S: GpuType
GPU_TYPE_NVIDIA_B200: GpuType
CLOUD_CLUSTER_STATUS_UNSPECIFIED: CloudClusterStatus
CLOUD_CLUSTER_STATUS_PENDING: CloudClusterStatus
CLOUD_CLUSTER_STATUS_ACTIVE: CloudClusterStatus
CLOUD_CLUSTER_STATUS_FAILED: CloudClusterStatus
CLOUD_CLUSTER_STATUS_TERMINATED: CloudClusterStatus
CLUSTER_TYPE_UNSPECIFIED: ClusterType
CLUSTER_TYPE_ON_PREMISE: ClusterType
CLUSTER_TYPE_CLOUD: ClusterType
CLUSTER_SCHEDULING_POLICY_UNSPECIFIED: ClusterSchedulingPolicy
CLUSTER_SCHEDULING_POLICY_EAGER: ClusterSchedulingPolicy
CLUSTER_SCHEDULING_POLICY_STRICT_PRIORITY_BACKFILL_PREEMPTIBLE_ONLY: ClusterSchedulingPolicy
CLUSTER_SCHEDULING_POLICY_STRICT_PRIORITY_BACKFILL_ALL: ClusterSchedulingPolicy
JOB_KIND_UNSPECIFIED: JobKind
JOB_KIND_BATCH: JobKind
JOB_KIND_SESSION: JobKind
STATUS_UNSPECIFIED: WorkloadStatus
STATUS_SUBMITTED: WorkloadStatus
STATUS_QUEUED: WorkloadStatus
STATUS_INITIALIZING: WorkloadStatus
STATUS_RUNNING: WorkloadStatus
STATUS_STOPPING: WorkloadStatus
STATUS_UPLOADING_RESULTS: WorkloadStatus
STATUS_CANCELED: WorkloadStatus
STATUS_SUCCEEDED: WorkloadStatus
STATUS_FAILED: WorkloadStatus
STATUS_READY_TO_START: WorkloadStatus
CANCELATION_CODE_UNSPECIFIED: CancelationCode
CANCELATION_CODE_SYSTEM_PREEMPTION: CancelationCode
CANCELATION_CODE_USER_PREEMPTION: CancelationCode
CANCELATION_CODE_IDLE: CancelationCode
CANCELATION_CODE_MANUAL: CancelationCode
CANCELATION_CODE_TIMEOUT: CancelationCode
CANCELATION_CODE_NODE_UNAVAILABLE: CancelationCode
CANCELATION_CODE_IMPOSSIBLE_TO_SCHEDULE: CancelationCode
CANCELATION_CODE_SIBLING_TASK_FAILED: CancelationCode
CANCELATION_CODE_SIBLING_TASK_PREEMPTION: CancelationCode
CANCELATION_CODE_HEALTHCHECK_FAILED: CancelationCode
CANCELATION_CODE_SIBLING_TASK_RETRY: CancelationCode
JOB_PLACEMENT_CONSTRAINT_TYPE_UNSPECIFIED: JobPlacementConstraintType
JOB_PLACEMENT_CONSTRAINT_TYPE_CLUSTER: JobPlacementConstraintType
JOB_PLACEMENT_CONSTRAINT_TYPE_HOSTNAME: JobPlacementConstraintType
JOB_PRIORITY_UNSPECIFIED: JobPriority
JOB_PRIORITY_LOW: JobPriority
JOB_PRIORITY_NORMAL: JobPriority
JOB_PRIORITY_HIGH: JobPriority
JOB_PRIORITY_URGENT: JobPriority
WORKLOAD_TYPE_UNSPECIFIED: WorkloadType
WORKLOAD_TYPE_EXPERIMENT: WorkloadType
WORKLOAD_TYPE_ENVIRONMENT: WorkloadType

class Interval(_message.Message):
    __slots__ = ("start", "finish")
    START_FIELD_NUMBER: _ClassVar[int]
    FINISH_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    finish: _timestamp_pb2.Timestamp
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finish: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "created", "name", "display_name", "pronouns", "user_details")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PRONOUNS_FIELD_NUMBER: _ClassVar[int]
    USER_DETAILS_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: _timestamp_pb2.Timestamp
    name: str
    display_name: str
    pronouns: str
    user_details: UserDetails
    def __init__(self, id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., display_name: _Optional[str] = ..., pronouns: _Optional[str] = ..., user_details: _Optional[_Union[UserDetails, _Mapping]] = ...) -> None: ...

class UserDetails(_message.Message):
    __slots__ = ("email", "role", "report_group")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    REPORT_GROUP_FIELD_NUMBER: _ClassVar[int]
    email: str
    role: AuthRole
    report_group: str
    def __init__(self, email: _Optional[str] = ..., role: _Optional[_Union[AuthRole, str]] = ..., report_group: _Optional[str] = ...) -> None: ...

class Organization(_message.Message):
    __slots__ = ("id", "created", "name", "display_name", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: _timestamp_pb2.Timestamp
    name: str
    display_name: str
    description: str
    def __init__(self, id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Workspace(_message.Message):
    __slots__ = ("id", "created", "name", "description", "owner_org", "owner_user", "author_org", "author_user", "modified", "archived", "size", "maximum_workload_priority", "budget_id", "slot_limit_preemptible", "slot_limit_non_preemptible", "assigned_slots_preemptible", "assigned_slots_non_preemptible")
    class WorkspaceItemCount(_message.Message):
        __slots__ = ("datasets", "experiments", "groups", "images", "environments")
        DATASETS_FIELD_NUMBER: _ClassVar[int]
        EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
        GROUPS_FIELD_NUMBER: _ClassVar[int]
        IMAGES_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
        datasets: int
        experiments: int
        groups: int
        images: int
        environments: int
        def __init__(self, datasets: _Optional[int] = ..., experiments: _Optional[int] = ..., groups: _Optional[int] = ..., images: _Optional[int] = ..., environments: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OWNER_ORG_FIELD_NUMBER: _ClassVar[int]
    OWNER_USER_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ORG_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_USER_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_WORKLOAD_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_LIMIT_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    SLOT_LIMIT_NON_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_SLOTS_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_SLOTS_NON_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: _timestamp_pb2.Timestamp
    name: str
    description: str
    owner_org: Organization
    owner_user: User
    author_org: Organization
    author_user: User
    modified: _timestamp_pb2.Timestamp
    archived: bool
    size: Workspace.WorkspaceItemCount
    maximum_workload_priority: JobPriority
    budget_id: str
    slot_limit_preemptible: int
    slot_limit_non_preemptible: int
    assigned_slots_preemptible: int
    assigned_slots_non_preemptible: int
    def __init__(self, id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., owner_org: _Optional[_Union[Organization, _Mapping]] = ..., owner_user: _Optional[_Union[User, _Mapping]] = ..., author_org: _Optional[_Union[Organization, _Mapping]] = ..., author_user: _Optional[_Union[User, _Mapping]] = ..., modified: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., archived: bool = ..., size: _Optional[_Union[Workspace.WorkspaceItemCount, _Mapping]] = ..., maximum_workload_priority: _Optional[_Union[JobPriority, str]] = ..., budget_id: _Optional[str] = ..., slot_limit_preemptible: _Optional[int] = ..., slot_limit_non_preemptible: _Optional[int] = ..., assigned_slots_preemptible: _Optional[int] = ..., assigned_slots_non_preemptible: _Optional[int] = ...) -> None: ...

class NodeShape(_message.Message):
    __slots__ = ("cpu_count", "memory_bytes", "gpu_count", "gpu_type")
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    GPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    GPU_TYPE_FIELD_NUMBER: _ClassVar[int]
    cpu_count: int
    memory_bytes: int
    gpu_count: int
    gpu_type: GpuType
    def __init__(self, cpu_count: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., gpu_count: _Optional[int] = ..., gpu_type: _Optional[_Union[GpuType, str]] = ...) -> None: ...

class SlotDetails(_message.Message):
    __slots__ = ("slot_count", "gpu_count", "cpu_count", "memory_bytes")
    SLOT_COUNT_FIELD_NUMBER: _ClassVar[int]
    GPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    slot_count: int
    gpu_count: int
    cpu_count: float
    memory_bytes: int
    def __init__(self, slot_count: _Optional[int] = ..., gpu_count: _Optional[int] = ..., cpu_count: _Optional[float] = ..., memory_bytes: _Optional[int] = ...) -> None: ...

class NodeResources(_message.Message):
    __slots__ = ("cpu_count", "memory_bytes", "gpu_ids", "gpu_type", "slot_details")
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    GPU_IDS_FIELD_NUMBER: _ClassVar[int]
    GPU_TYPE_FIELD_NUMBER: _ClassVar[int]
    SLOT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    cpu_count: int
    memory_bytes: int
    gpu_ids: _containers.RepeatedScalarFieldContainer[str]
    gpu_type: GpuType
    slot_details: SlotDetails
    def __init__(self, cpu_count: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., gpu_ids: _Optional[_Iterable[str]] = ..., gpu_type: _Optional[_Union[GpuType, str]] = ..., slot_details: _Optional[_Union[SlotDetails, _Mapping]] = ...) -> None: ...

class NodeRequest(_message.Message):
    __slots__ = ("cpu_count", "memory_bytes", "gpu_count", "gpu_type")
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    GPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    GPU_TYPE_FIELD_NUMBER: _ClassVar[int]
    cpu_count: int
    memory_bytes: int
    gpu_count: int
    gpu_type: GpuType
    def __init__(self, cpu_count: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., gpu_count: _Optional[int] = ..., gpu_type: _Optional[_Union[GpuType, str]] = ...) -> None: ...

class OnPremiseClusterDetails(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CloudClusterDetails(_message.Message):
    __slots__ = ("status", "validated", "status_message", "capacity", "node_cost", "preemptible_nodes", "compute_source", "node_request")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VALIDATED_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    NODE_COST_FIELD_NUMBER: _ClassVar[int]
    PREEMPTIBLE_NODES_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    NODE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    status: CloudClusterStatus
    validated: _timestamp_pb2.Timestamp
    status_message: str
    capacity: int
    node_cost: float
    preemptible_nodes: bool
    compute_source: str
    node_request: NodeRequest
    def __init__(self, status: _Optional[_Union[CloudClusterStatus, str]] = ..., validated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status_message: _Optional[str] = ..., capacity: _Optional[int] = ..., node_cost: _Optional[float] = ..., preemptible_nodes: bool = ..., compute_source: _Optional[str] = ..., node_request: _Optional[_Union[NodeRequest, _Mapping]] = ...) -> None: ...

class Cluster(_message.Message):
    __slots__ = ("id", "created", "name", "organization_id", "on_premise_details", "cloud_details", "node_shape", "max_session_timeout", "user_restrictions", "allow_preemptible_restriction_exceptions", "organization_name", "require_preemptible_tasks", "cluster_occupancy", "node_count", "scheduling_policy", "max_task_timeout", "cluster_job_queue_size")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ON_PREMISE_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    NODE_SHAPE_FIELD_NUMBER: _ClassVar[int]
    MAX_SESSION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    USER_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PREEMPTIBLE_RESTRICTION_EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_PREEMPTIBLE_TASKS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_OCCUPANCY_FIELD_NUMBER: _ClassVar[int]
    NODE_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCHEDULING_POLICY_FIELD_NUMBER: _ClassVar[int]
    MAX_TASK_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_JOB_QUEUE_SIZE_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: _timestamp_pb2.Timestamp
    name: str
    organization_id: str
    on_premise_details: OnPremiseClusterDetails
    cloud_details: CloudClusterDetails
    node_shape: NodeShape
    max_session_timeout: _duration_pb2.Duration
    user_restrictions: _containers.RepeatedScalarFieldContainer[str]
    allow_preemptible_restriction_exceptions: bool
    organization_name: str
    require_preemptible_tasks: bool
    cluster_occupancy: ClusterOccupancy
    node_count: int
    scheduling_policy: ClusterSchedulingPolicy
    max_task_timeout: _duration_pb2.Duration
    cluster_job_queue_size: int
    def __init__(self, id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., organization_id: _Optional[str] = ..., on_premise_details: _Optional[_Union[OnPremiseClusterDetails, _Mapping]] = ..., cloud_details: _Optional[_Union[CloudClusterDetails, _Mapping]] = ..., node_shape: _Optional[_Union[NodeShape, _Mapping]] = ..., max_session_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., user_restrictions: _Optional[_Iterable[str]] = ..., allow_preemptible_restriction_exceptions: bool = ..., organization_name: _Optional[str] = ..., require_preemptible_tasks: bool = ..., cluster_occupancy: _Optional[_Union[ClusterOccupancy, _Mapping]] = ..., node_count: _Optional[int] = ..., scheduling_policy: _Optional[_Union[ClusterSchedulingPolicy, str]] = ..., max_task_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., cluster_job_queue_size: _Optional[int] = ...) -> None: ...

class SlotCounts(_message.Message):
    __slots__ = ("total", "available", "occupied", "assigned", "cordoned")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    OCCUPIED_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_FIELD_NUMBER: _ClassVar[int]
    CORDONED_FIELD_NUMBER: _ClassVar[int]
    total: int
    available: int
    occupied: int
    assigned: int
    cordoned: int
    def __init__(self, total: _Optional[int] = ..., available: _Optional[int] = ..., occupied: _Optional[int] = ..., assigned: _Optional[int] = ..., cordoned: _Optional[int] = ...) -> None: ...

class ClusterOccupancy(_message.Message):
    __slots__ = ("running_jobs_count", "slot_counts", "node_occupancies")
    RUNNING_JOBS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SLOT_COUNTS_FIELD_NUMBER: _ClassVar[int]
    NODE_OCCUPANCIES_FIELD_NUMBER: _ClassVar[int]
    running_jobs_count: int
    slot_counts: SlotCounts
    node_occupancies: _containers.RepeatedCompositeFieldContainer[NodeOccupancy]
    def __init__(self, running_jobs_count: _Optional[int] = ..., slot_counts: _Optional[_Union[SlotCounts, _Mapping]] = ..., node_occupancies: _Optional[_Iterable[_Union[NodeOccupancy, _Mapping]]] = ...) -> None: ...

class SlotGroups(_message.Message):
    __slots__ = ("budget_reference", "workspace_reference", "user_reference", "job_priority", "workload_count", "job_count")
    BUDGET_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    USER_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    JOB_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    WORKLOAD_COUNT_FIELD_NUMBER: _ClassVar[int]
    JOB_COUNT_FIELD_NUMBER: _ClassVar[int]
    budget_reference: str
    workspace_reference: str
    user_reference: str
    job_priority: JobPriority
    workload_count: int
    job_count: int
    def __init__(self, budget_reference: _Optional[str] = ..., workspace_reference: _Optional[str] = ..., user_reference: _Optional[str] = ..., job_priority: _Optional[_Union[JobPriority, str]] = ..., workload_count: _Optional[int] = ..., job_count: _Optional[int] = ...) -> None: ...

class ClusterSlotUsage(_message.Message):
    __slots__ = ("assigned", "available", "cordoned", "slot_seconds")
    ASSIGNED_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CORDONED_FIELD_NUMBER: _ClassVar[int]
    SLOT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    assigned: SlotGroups
    available: _empty_pb2.Empty
    cordoned: bool
    slot_seconds: int
    def __init__(self, assigned: _Optional[_Union[SlotGroups, _Mapping]] = ..., available: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., cordoned: bool = ..., slot_seconds: _Optional[int] = ...) -> None: ...

class NodeOccupancy(_message.Message):
    __slots__ = ("node_id", "running_jobs_count", "slot_counts")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNING_JOBS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SLOT_COUNTS_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    running_jobs_count: int
    slot_counts: SlotCounts
    def __init__(self, node_id: _Optional[str] = ..., running_jobs_count: _Optional[int] = ..., slot_counts: _Optional[_Union[SlotCounts, _Mapping]] = ...) -> None: ...

class CordonDetails(_message.Message):
    __slots__ = ("cordoned", "cordon_reason", "cordon_agent_id")
    CORDONED_FIELD_NUMBER: _ClassVar[int]
    CORDON_REASON_FIELD_NUMBER: _ClassVar[int]
    CORDON_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    cordoned: _timestamp_pb2.Timestamp
    cordon_reason: str
    cordon_agent_id: str
    def __init__(self, cordoned: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cordon_reason: _Optional[str] = ..., cordon_agent_id: _Optional[str] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("id", "created", "cluster_id", "hostname", "expiry", "cordon_details", "node_resources", "account_id", "heartbeat")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    CORDON_DETAILS_FIELD_NUMBER: _ClassVar[int]
    NODE_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: _timestamp_pb2.Timestamp
    cluster_id: str
    hostname: str
    expiry: _timestamp_pb2.Timestamp
    cordon_details: CordonDetails
    node_resources: NodeResources
    account_id: str
    heartbeat: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cluster_id: _Optional[str] = ..., hostname: _Optional[str] = ..., expiry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cordon_details: _Optional[_Union[CordonDetails, _Mapping]] = ..., node_resources: _Optional[_Union[NodeResources, _Mapping]] = ..., account_id: _Optional[str] = ..., heartbeat: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JobStatus(_message.Message):
    __slots__ = ("status", "created", "scheduled", "started", "exited", "failed", "finalized", "canceled", "exit_code", "message", "canceled_for", "canceled_code", "idle_since", "ready", "failed_scheduling_message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    EXITED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    FINALIZED_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FOR_FIELD_NUMBER: _ClassVar[int]
    CANCELED_CODE_FIELD_NUMBER: _ClassVar[int]
    IDLE_SINCE_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    FAILED_SCHEDULING_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: WorkloadStatus
    created: _timestamp_pb2.Timestamp
    scheduled: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    exited: _timestamp_pb2.Timestamp
    failed: _timestamp_pb2.Timestamp
    finalized: _timestamp_pb2.Timestamp
    canceled: _timestamp_pb2.Timestamp
    exit_code: int
    message: str
    canceled_for: str
    canceled_code: CancelationCode
    idle_since: _timestamp_pb2.Timestamp
    ready: _timestamp_pb2.Timestamp
    failed_scheduling_message: str
    def __init__(self, status: _Optional[_Union[WorkloadStatus, str]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., scheduled: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exited: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., failed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finalized: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., canceled: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exit_code: _Optional[int] = ..., message: _Optional[str] = ..., canceled_for: _Optional[str] = ..., canceled_code: _Optional[_Union[CancelationCode, str]] = ..., idle_since: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ready: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., failed_scheduling_message: _Optional[str] = ...) -> None: ...

class ResourceRequest(_message.Message):
    __slots__ = ("cpu_count", "memory_bytes", "gpu_count", "shared_memory_bytes")
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    GPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    SHARED_MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    cpu_count: float
    memory_bytes: int
    gpu_count: int
    shared_memory_bytes: int
    def __init__(self, cpu_count: _Optional[float] = ..., memory_bytes: _Optional[int] = ..., gpu_count: _Optional[int] = ..., shared_memory_bytes: _Optional[int] = ...) -> None: ...

class ResourceAssignment(_message.Message):
    __slots__ = ("cpu_count", "memory_bytes", "gpus", "assigned_slots_count")
    CPU_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_SLOTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    cpu_count: float
    memory_bytes: int
    gpus: _containers.RepeatedScalarFieldContainer[str]
    assigned_slots_count: int
    def __init__(self, cpu_count: _Optional[float] = ..., memory_bytes: _Optional[int] = ..., gpus: _Optional[_Iterable[str]] = ..., assigned_slots_count: _Optional[int] = ...) -> None: ...

class PortMapping(_message.Message):
    __slots__ = ("container_port", "host_port")
    CONTAINER_PORT_FIELD_NUMBER: _ClassVar[int]
    HOST_PORT_FIELD_NUMBER: _ClassVar[int]
    container_port: int
    host_port: int
    def __init__(self, container_port: _Optional[int] = ..., host_port: _Optional[int] = ...) -> None: ...

class EnvironmentVariable(_message.Message):
    __slots__ = ("name", "literal", "secret_reference")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LITERAL_FIELD_NUMBER: _ClassVar[int]
    SECRET_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    literal: str
    secret_reference: str
    def __init__(self, name: _Optional[str] = ..., literal: _Optional[str] = ..., secret_reference: _Optional[str] = ...) -> None: ...

class Mount(_message.Message):
    __slots__ = ("mount_path", "sub_path", "dataset_id", "host_path", "secret_reference", "weka")
    MOUNT_PATH_FIELD_NUMBER: _ClassVar[int]
    SUB_PATH_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    HOST_PATH_FIELD_NUMBER: _ClassVar[int]
    SECRET_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    WEKA_FIELD_NUMBER: _ClassVar[int]
    mount_path: str
    sub_path: str
    dataset_id: str
    host_path: str
    secret_reference: str
    weka: str
    def __init__(self, mount_path: _Optional[str] = ..., sub_path: _Optional[str] = ..., dataset_id: _Optional[str] = ..., host_path: _Optional[str] = ..., secret_reference: _Optional[str] = ..., weka: _Optional[str] = ...) -> None: ...

class JobPlacementConstraint(_message.Message):
    __slots__ = ("type", "values")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    type: JobPlacementConstraintType
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[JobPlacementConstraintType, str]] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class JobIdentity(_message.Message):
    __slots__ = ("type",)
    class JobIdentityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        JOB_IDENTITY_TYPE_UNSPECIFIED: _ClassVar[JobIdentity.JobIdentityType]
        JOB_IDENTITY_TYPE_NONE: _ClassVar[JobIdentity.JobIdentityType]
        JOB_IDENTITY_TYPE_HOST: _ClassVar[JobIdentity.JobIdentityType]
    JOB_IDENTITY_TYPE_UNSPECIFIED: JobIdentity.JobIdentityType
    JOB_IDENTITY_TYPE_NONE: JobIdentity.JobIdentityType
    JOB_IDENTITY_TYPE_HOST: JobIdentity.JobIdentityType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: JobIdentity.JobIdentityType
    def __init__(self, type: _Optional[_Union[JobIdentity.JobIdentityType, str]] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("id", "task_id", "environment_id", "name", "author_id", "workspace_id", "status", "container_spec", "system_details", "assignment_details", "workload_id", "metrics", "workspace_reference", "author_reference", "retry_ancestor_id", "budget_id", "workload_created")
    ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_SPEC_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_DETAILS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    WORKLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    RETRY_ANCESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    WORKLOAD_CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    task_id: str
    environment_id: str
    name: str
    author_id: str
    workspace_id: str
    status: JobStatus
    container_spec: ContainerSpec
    system_details: SystemDetails
    assignment_details: AssignmentDetails
    workload_id: str
    metrics: _struct_pb2.Struct
    workspace_reference: str
    author_reference: str
    retry_ancestor_id: str
    budget_id: str
    workload_created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., task_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., name: _Optional[str] = ..., author_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., status: _Optional[_Union[JobStatus, _Mapping]] = ..., container_spec: _Optional[_Union[ContainerSpec, _Mapping]] = ..., system_details: _Optional[_Union[SystemDetails, _Mapping]] = ..., assignment_details: _Optional[_Union[AssignmentDetails, _Mapping]] = ..., workload_id: _Optional[str] = ..., metrics: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., workspace_reference: _Optional[str] = ..., author_reference: _Optional[str] = ..., retry_ancestor_id: _Optional[str] = ..., budget_id: _Optional[str] = ..., workload_created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IdleJob(_message.Message):
    __slots__ = ("id", "idle_since")
    ID_FIELD_NUMBER: _ClassVar[int]
    IDLE_SINCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    idle_since: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., idle_since: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ContainerSpec(_message.Message):
    __slots__ = ("resource_request", "image_id", "docker_reference", "command", "arguments", "environment_variables", "mounts", "save_image", "working_directory", "result_path", "port_mapping_request", "host_networking", "identity")
    RESOURCE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    DOCKER_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    SAVE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    RESULT_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_MAPPING_REQUEST_FIELD_NUMBER: _ClassVar[int]
    HOST_NETWORKING_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    resource_request: ResourceRequest
    image_id: str
    docker_reference: str
    command: _containers.RepeatedScalarFieldContainer[str]
    arguments: _containers.RepeatedScalarFieldContainer[str]
    environment_variables: _containers.RepeatedCompositeFieldContainer[EnvironmentVariable]
    mounts: _containers.RepeatedCompositeFieldContainer[Mount]
    save_image: bool
    working_directory: str
    result_path: str
    port_mapping_request: _containers.RepeatedCompositeFieldContainer[PortMapping]
    host_networking: bool
    identity: JobIdentity
    def __init__(self, resource_request: _Optional[_Union[ResourceRequest, _Mapping]] = ..., image_id: _Optional[str] = ..., docker_reference: _Optional[str] = ..., command: _Optional[_Iterable[str]] = ..., arguments: _Optional[_Iterable[str]] = ..., environment_variables: _Optional[_Iterable[_Union[EnvironmentVariable, _Mapping]]] = ..., mounts: _Optional[_Iterable[_Union[Mount, _Mapping]]] = ..., save_image: bool = ..., working_directory: _Optional[str] = ..., result_path: _Optional[str] = ..., port_mapping_request: _Optional[_Iterable[_Union[PortMapping, _Mapping]]] = ..., host_networking: bool = ..., identity: _Optional[_Union[JobIdentity, _Mapping]] = ...) -> None: ...

class ReplicaGroupDetails(_message.Message):
    __slots__ = ("id", "size", "rank", "is_leader_replica", "synchronized_start_timeout")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    IS_LEADER_REPLICA_FIELD_NUMBER: _ClassVar[int]
    SYNCHRONIZED_START_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    id: str
    size: int
    rank: int
    is_leader_replica: bool
    synchronized_start_timeout: _duration_pb2.Duration
    def __init__(self, id: _Optional[str] = ..., size: _Optional[int] = ..., rank: _Optional[int] = ..., is_leader_replica: bool = ..., synchronized_start_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SystemDetails(_message.Message):
    __slots__ = ("priority", "preemptible", "timeout", "placement_constraints", "replica_group_details", "propagate_failure", "propagate_preemption")
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    REPLICA_GROUP_DETAILS_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_FAILURE_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_PREEMPTION_FIELD_NUMBER: _ClassVar[int]
    priority: JobPriority
    preemptible: bool
    timeout: _duration_pb2.Duration
    placement_constraints: _containers.RepeatedCompositeFieldContainer[JobPlacementConstraint]
    replica_group_details: ReplicaGroupDetails
    propagate_failure: bool
    propagate_preemption: bool
    def __init__(self, priority: _Optional[_Union[JobPriority, str]] = ..., preemptible: bool = ..., timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., placement_constraints: _Optional[_Iterable[_Union[JobPlacementConstraint, _Mapping]]] = ..., replica_group_details: _Optional[_Union[ReplicaGroupDetails, _Mapping]] = ..., propagate_failure: bool = ..., propagate_preemption: bool = ...) -> None: ...

class AssignmentDetails(_message.Message):
    __slots__ = ("node_id", "resource_assignment", "port_mapping_assignment", "result_dataset_id", "assigned_environment_variables", "occupied_slots_count")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    PORT_MAPPING_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    OCCUPIED_SLOTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    resource_assignment: ResourceAssignment
    port_mapping_assignment: _containers.RepeatedCompositeFieldContainer[PortMapping]
    result_dataset_id: str
    assigned_environment_variables: _containers.RepeatedCompositeFieldContainer[EnvironmentVariable]
    occupied_slots_count: int
    def __init__(self, node_id: _Optional[str] = ..., resource_assignment: _Optional[_Union[ResourceAssignment, _Mapping]] = ..., port_mapping_assignment: _Optional[_Iterable[_Union[PortMapping, _Mapping]]] = ..., result_dataset_id: _Optional[str] = ..., assigned_environment_variables: _Optional[_Iterable[_Union[EnvironmentVariable, _Mapping]]] = ..., occupied_slots_count: _Optional[int] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("id", "experiment_id", "name", "author_id", "created", "container_spec", "system_details", "status", "idle_job")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_SPEC_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IDLE_JOB_FIELD_NUMBER: _ClassVar[int]
    id: str
    experiment_id: str
    name: str
    author_id: str
    created: _timestamp_pb2.Timestamp
    container_spec: ContainerSpec
    system_details: SystemDetails
    status: WorkloadStatus
    idle_job: IdleJob
    def __init__(self, id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., name: _Optional[str] = ..., author_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., container_spec: _Optional[_Union[ContainerSpec, _Mapping]] = ..., system_details: _Optional[_Union[SystemDetails, _Mapping]] = ..., status: _Optional[_Union[WorkloadStatus, str]] = ..., idle_job: _Optional[_Union[IdleJob, _Mapping]] = ...) -> None: ...

class Experiment(_message.Message):
    __slots__ = ("id", "name", "author_id", "workspace_id", "description", "tasks", "created", "canceled", "canceled_for")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    author_id: str
    workspace_id: str
    description: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    created: _timestamp_pb2.Timestamp
    canceled: _timestamp_pb2.Timestamp
    canceled_for: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., author_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., description: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., canceled: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., canceled_for: _Optional[str] = ...) -> None: ...

class Environment(_message.Message):
    __slots__ = ("id", "name", "author_id", "workspace_id", "created", "container_spec", "system_details", "idle_job")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_SPEC_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_DETAILS_FIELD_NUMBER: _ClassVar[int]
    IDLE_JOB_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    author_id: str
    workspace_id: str
    created: _timestamp_pb2.Timestamp
    container_spec: ContainerSpec
    system_details: SystemDetails
    idle_job: IdleJob
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., author_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., container_spec: _Optional[_Union[ContainerSpec, _Mapping]] = ..., system_details: _Optional[_Union[SystemDetails, _Mapping]] = ..., idle_job: _Optional[_Union[IdleJob, _Mapping]] = ...) -> None: ...

class Workload(_message.Message):
    __slots__ = ("experiment", "environment", "status", "budget_id")
    EXPERIMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    experiment: Experiment
    environment: Environment
    status: WorkloadStatus
    budget_id: str
    def __init__(self, experiment: _Optional[_Union[Experiment, _Mapping]] = ..., environment: _Optional[_Union[Environment, _Mapping]] = ..., status: _Optional[_Union[WorkloadStatus, str]] = ..., budget_id: _Optional[str] = ...) -> None: ...

class JobAssignment(_message.Message):
    __slots__ = ("job_id", "assignment_details", "estimated_scheduled_time")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_SCHEDULED_TIME_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    assignment_details: AssignmentDetails
    estimated_scheduled_time: _timestamp_pb2.Timestamp
    def __init__(self, job_id: _Optional[str] = ..., assignment_details: _Optional[_Union[AssignmentDetails, _Mapping]] = ..., estimated_scheduled_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JobCancelation(_message.Message):
    __slots__ = ("job_id", "canceled_code", "canceled_for")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELED_CODE_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FOR_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    canceled_code: CancelationCode
    canceled_for: str
    def __init__(self, job_id: _Optional[str] = ..., canceled_code: _Optional[_Union[CancelationCode, str]] = ..., canceled_for: _Optional[str] = ...) -> None: ...

class JobEvent(_message.Message):
    __slots__ = ("id", "job_id", "created", "occurred", "status", "message")
    ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    job_id: str
    created: _timestamp_pb2.Timestamp
    occurred: _timestamp_pb2.Timestamp
    status: str
    message: str
    def __init__(self, id: _Optional[str] = ..., job_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., occurred: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class SummarizedJobEvent(_message.Message):
    __slots__ = ("job_id", "status", "occurrences", "earliest_occurrence", "latest_occurrence", "latest_message")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OCCURRENCES_FIELD_NUMBER: _ClassVar[int]
    EARLIEST_OCCURRENCE_FIELD_NUMBER: _ClassVar[int]
    LATEST_OCCURRENCE_FIELD_NUMBER: _ClassVar[int]
    LATEST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: str
    occurrences: int
    earliest_occurrence: _timestamp_pb2.Timestamp
    latest_occurrence: _timestamp_pb2.Timestamp
    latest_message: str
    def __init__(self, job_id: _Optional[str] = ..., status: _Optional[str] = ..., occurrences: _Optional[int] = ..., earliest_occurrence: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., latest_occurrence: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., latest_message: _Optional[str] = ...) -> None: ...

class JobLog(_message.Message):
    __slots__ = ("timestamp", "message")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    message: bytes
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[bytes] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("id", "name", "full_name", "workspace_id", "author_id", "created", "committed", "docker_id", "docker_tag", "original_tag", "description", "source_job_id", "size")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_FIELD_NUMBER: _ClassVar[int]
    DOCKER_ID_FIELD_NUMBER: _ClassVar[int]
    DOCKER_TAG_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_TAG_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    workspace_id: str
    author_id: str
    created: _timestamp_pb2.Timestamp
    committed: _timestamp_pb2.Timestamp
    docker_id: str
    docker_tag: str
    original_tag: str
    description: str
    source_job_id: str
    size: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., workspace_id: _Optional[str] = ..., author_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., committed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., docker_id: _Optional[str] = ..., docker_tag: _Optional[str] = ..., original_tag: _Optional[str] = ..., description: _Optional[str] = ..., source_job_id: _Optional[str] = ..., size: _Optional[int] = ...) -> None: ...

class Secret(_message.Message):
    __slots__ = ("name", "created", "updated", "author_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    author_id: str
    def __init__(self, name: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., author_id: _Optional[str] = ...) -> None: ...

class Dataset(_message.Message):
    __slots__ = ("id", "name", "full_name", "author_id", "workspace_id", "created", "committed", "description", "source_execution")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_EXECUTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    author_id: str
    workspace_id: str
    created: _timestamp_pb2.Timestamp
    committed: _timestamp_pb2.Timestamp
    description: str
    source_execution: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., author_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., committed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ..., source_execution: _Optional[str] = ...) -> None: ...

class DatasetStorage(_message.Message):
    __slots__ = ("url", "total_size", "file_count", "token", "token_expires")
    URL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_EXPIRES_FIELD_NUMBER: _ClassVar[int]
    url: str
    total_size: int
    file_count: int
    token: str
    token_expires: _timestamp_pb2.Timestamp
    def __init__(self, url: _Optional[str] = ..., total_size: _Optional[int] = ..., file_count: _Optional[int] = ..., token: _Optional[str] = ..., token_expires: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DatasetFile(_message.Message):
    __slots__ = ("path", "size", "updated", "digest")
    class AlgorithmType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALGORITHM_TYPE_UNSPECIFIED: _ClassVar[DatasetFile.AlgorithmType]
        ALGORITHM_TYPE_SHA256: _ClassVar[DatasetFile.AlgorithmType]
        ALGORITHM_TYPE_CRC32C: _ClassVar[DatasetFile.AlgorithmType]
    ALGORITHM_TYPE_UNSPECIFIED: DatasetFile.AlgorithmType
    ALGORITHM_TYPE_SHA256: DatasetFile.AlgorithmType
    ALGORITHM_TYPE_CRC32C: DatasetFile.AlgorithmType
    class Digest(_message.Message):
        __slots__ = ("algorithm", "value")
        ALGORITHM_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        algorithm: DatasetFile.AlgorithmType
        value: bytes
        def __init__(self, algorithm: _Optional[_Union[DatasetFile.AlgorithmType, str]] = ..., value: _Optional[bytes] = ...) -> None: ...
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    path: str
    size: int
    updated: _timestamp_pb2.Timestamp
    digest: DatasetFile.Digest
    def __init__(self, path: _Optional[str] = ..., size: _Optional[int] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., digest: _Optional[_Union[DatasetFile.Digest, _Mapping]] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ("id", "name", "full_name", "description", "workspace_id", "author_id", "created", "modified", "group_parameters_available", "group_parameters_selected")
    class GroupParameterWithCount(_message.Message):
        __slots__ = ("group_parameter", "count")
        GROUP_PARAMETER_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        group_parameter: GroupParameter
        count: int
        def __init__(self, group_parameter: _Optional[_Union[GroupParameter, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FIELD_NUMBER: _ClassVar[int]
    GROUP_PARAMETERS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    GROUP_PARAMETERS_SELECTED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    description: str
    workspace_id: str
    author_id: str
    created: _timestamp_pb2.Timestamp
    modified: _timestamp_pb2.Timestamp
    group_parameters_available: _containers.RepeatedCompositeFieldContainer[Group.GroupParameterWithCount]
    group_parameters_selected: _containers.RepeatedCompositeFieldContainer[GroupParameter]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., description: _Optional[str] = ..., workspace_id: _Optional[str] = ..., author_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modified: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., group_parameters_available: _Optional[_Iterable[_Union[Group.GroupParameterWithCount, _Mapping]]] = ..., group_parameters_selected: _Optional[_Iterable[_Union[GroupParameter, _Mapping]]] = ...) -> None: ...

class GroupParameter(_message.Message):
    __slots__ = ("type", "name")
    class GroupParameterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GROUP_PARAMETER_TYPE_UNSPECIFIED: _ClassVar[GroupParameter.GroupParameterType]
        GROUP_PARAMETER_ENV: _ClassVar[GroupParameter.GroupParameterType]
        GROUP_PARAMETER_METRIC: _ClassVar[GroupParameter.GroupParameterType]
    GROUP_PARAMETER_TYPE_UNSPECIFIED: GroupParameter.GroupParameterType
    GROUP_PARAMETER_ENV: GroupParameter.GroupParameterType
    GROUP_PARAMETER_METRIC: GroupParameter.GroupParameterType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    type: GroupParameter.GroupParameterType
    name: str
    def __init__(self, type: _Optional[_Union[GroupParameter.GroupParameterType, str]] = ..., name: _Optional[str] = ...) -> None: ...

class TaskMetrics(_message.Message):
    __slots__ = ("task_id", "task_name", "experiment_id", "experiment_name", "task_status", "metrics")
    class Metric(_message.Message):
        __slots__ = ("group_parameter", "value")
        GROUP_PARAMETER_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        group_parameter: GroupParameter
        value: _struct_pb2.Value
        def __init__(self, group_parameter: _Optional[_Union[GroupParameter, _Mapping]] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    task_name: str
    experiment_id: str
    experiment_name: str
    task_status: WorkloadStatus
    metrics: _containers.RepeatedCompositeFieldContainer[TaskMetrics.Metric]
    def __init__(self, task_id: _Optional[str] = ..., task_name: _Optional[str] = ..., experiment_id: _Optional[str] = ..., experiment_name: _Optional[str] = ..., task_status: _Optional[_Union[WorkloadStatus, str]] = ..., metrics: _Optional[_Iterable[_Union[TaskMetrics.Metric, _Mapping]]] = ...) -> None: ...

class SchedulerInput(_message.Message):
    __slots__ = ("non_finalized_jobs", "nodes", "clusters", "retry_ancestors", "workspaces")
    NON_FINALIZED_JOBS_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    RETRY_ANCESTORS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACES_FIELD_NUMBER: _ClassVar[int]
    non_finalized_jobs: _containers.RepeatedCompositeFieldContainer[Job]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    clusters: _containers.RepeatedCompositeFieldContainer[Cluster]
    retry_ancestors: _containers.RepeatedCompositeFieldContainer[Job]
    workspaces: _containers.RepeatedCompositeFieldContainer[Workspace]
    def __init__(self, non_finalized_jobs: _Optional[_Iterable[_Union[Job, _Mapping]]] = ..., nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ..., clusters: _Optional[_Iterable[_Union[Cluster, _Mapping]]] = ..., retry_ancestors: _Optional[_Iterable[_Union[Job, _Mapping]]] = ..., workspaces: _Optional[_Iterable[_Union[Workspace, _Mapping]]] = ...) -> None: ...

class SchedulerPassSummary(_message.Message):
    __slots__ = ("candidate_job_id", "filtered_nodes", "scored_nodes", "assignment", "cancelations", "skip_reasons")
    class FilterSummary(_message.Message):
        __slots__ = ("node_id", "filter_names")
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        FILTER_NAMES_FIELD_NUMBER: _ClassVar[int]
        node_id: str
        filter_names: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, node_id: _Optional[str] = ..., filter_names: _Optional[_Iterable[str]] = ...) -> None: ...
    class ScoreSummary(_message.Message):
        __slots__ = ("node_id", "score_function_scores")
        class ScoreFunctionScoresEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: int
            def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        SCORE_FUNCTION_SCORES_FIELD_NUMBER: _ClassVar[int]
        node_id: str
        score_function_scores: _containers.ScalarMap[str, int]
        def __init__(self, node_id: _Optional[str] = ..., score_function_scores: _Optional[_Mapping[str, int]] = ...) -> None: ...
    CANDIDATE_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERED_NODES_FIELD_NUMBER: _ClassVar[int]
    SCORED_NODES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    CANCELATIONS_FIELD_NUMBER: _ClassVar[int]
    SKIP_REASONS_FIELD_NUMBER: _ClassVar[int]
    candidate_job_id: str
    filtered_nodes: _containers.RepeatedCompositeFieldContainer[SchedulerPassSummary.FilterSummary]
    scored_nodes: _containers.RepeatedCompositeFieldContainer[SchedulerPassSummary.ScoreSummary]
    assignment: JobAssignment
    cancelations: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    skip_reasons: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, candidate_job_id: _Optional[str] = ..., filtered_nodes: _Optional[_Iterable[_Union[SchedulerPassSummary.FilterSummary, _Mapping]]] = ..., scored_nodes: _Optional[_Iterable[_Union[SchedulerPassSummary.ScoreSummary, _Mapping]]] = ..., assignment: _Optional[_Union[JobAssignment, _Mapping]] = ..., cancelations: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., skip_reasons: _Optional[_Iterable[str]] = ...) -> None: ...

class SchedulerSummary(_message.Message):
    __slots__ = ("timestamp", "job_cancelations", "sorted_unscheduled_job_ids", "passes", "total_assignment_count", "total_cancelation_count", "cluster_job_queues")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    JOB_CANCELATIONS_FIELD_NUMBER: _ClassVar[int]
    SORTED_UNSCHEDULED_JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    PASSES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ASSIGNMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CANCELATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_JOB_QUEUES_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    job_cancelations: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    sorted_unscheduled_job_ids: _containers.RepeatedScalarFieldContainer[str]
    passes: _containers.RepeatedCompositeFieldContainer[SchedulerPassSummary]
    total_assignment_count: int
    total_cancelation_count: int
    cluster_job_queues: _containers.RepeatedCompositeFieldContainer[ClusterJobQueue]
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., job_cancelations: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., sorted_unscheduled_job_ids: _Optional[_Iterable[str]] = ..., passes: _Optional[_Iterable[_Union[SchedulerPassSummary, _Mapping]]] = ..., total_assignment_count: _Optional[int] = ..., total_cancelation_count: _Optional[int] = ..., cluster_job_queues: _Optional[_Iterable[_Union[ClusterJobQueue, _Mapping]]] = ...) -> None: ...

class SchedulerUpdateBatch(_message.Message):
    __slots__ = ("node_id", "job_assignments", "job_cancelations", "job_reschedulings", "node_actions")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    JOB_CANCELATIONS_FIELD_NUMBER: _ClassVar[int]
    JOB_RESCHEDULINGS_FIELD_NUMBER: _ClassVar[int]
    NODE_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    job_assignments: _containers.RepeatedCompositeFieldContainer[JobAssignment]
    job_cancelations: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    job_reschedulings: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    node_actions: _containers.RepeatedCompositeFieldContainer[NodeAction]
    def __init__(self, node_id: _Optional[str] = ..., job_assignments: _Optional[_Iterable[_Union[JobAssignment, _Mapping]]] = ..., job_cancelations: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., job_reschedulings: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., node_actions: _Optional[_Iterable[_Union[NodeAction, _Mapping]]] = ...) -> None: ...

class SchedulerOutput(_message.Message):
    __slots__ = ("id", "organization_id", "summary", "failed_scheduling_job_events", "update_batches", "estimated_assignments")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    FAILED_SCHEDULING_JOB_EVENTS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_BATCHES_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    summary: SchedulerSummary
    failed_scheduling_job_events: _containers.RepeatedCompositeFieldContainer[CreateJobEventRequest]
    update_batches: _containers.RepeatedCompositeFieldContainer[SchedulerUpdateBatch]
    estimated_assignments: _containers.RepeatedCompositeFieldContainer[JobAssignment]
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., summary: _Optional[_Union[SchedulerSummary, _Mapping]] = ..., failed_scheduling_job_events: _Optional[_Iterable[_Union[CreateJobEventRequest, _Mapping]]] = ..., update_batches: _Optional[_Iterable[_Union[SchedulerUpdateBatch, _Mapping]]] = ..., estimated_assignments: _Optional[_Iterable[_Union[JobAssignment, _Mapping]]] = ...) -> None: ...

class SchedulerRun(_message.Message):
    __slots__ = ("input", "output")
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    input: SchedulerInput
    output: SchedulerOutput
    def __init__(self, input: _Optional[_Union[SchedulerInput, _Mapping]] = ..., output: _Optional[_Union[SchedulerOutput, _Mapping]] = ...) -> None: ...

class Budget(_message.Message):
    __slots__ = ("id", "organization_id", "name", "organization_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    name: str
    organization_name: str
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., name: _Optional[str] = ..., organization_name: _Optional[str] = ...) -> None: ...

class QueueWorkMetadata(_message.Message):
    __slots__ = ("queue_id", "work_id", "worker_id")
    QUEUE_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    queue_id: str
    work_id: str
    worker_id: str
    def __init__(self, queue_id: _Optional[str] = ..., work_id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class QueueWorkerInput(_message.Message):
    __slots__ = ("metadata", "input")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    metadata: QueueWorkMetadata
    input: _struct_pb2.Struct
    def __init__(self, metadata: _Optional[_Union[QueueWorkMetadata, _Mapping]] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class QueueWorkerOutput(_message.Message):
    __slots__ = ("metadata", "output", "error")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    metadata: QueueWorkMetadata
    output: _struct_pb2.Struct
    error: str
    def __init__(self, metadata: _Optional[_Union[QueueWorkMetadata, _Mapping]] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class CreateTokenForGoogleUIDRequest(_message.Message):
    __slots__ = ("google_uid", "user_email")
    GOOGLE_UID_FIELD_NUMBER: _ClassVar[int]
    USER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    google_uid: str
    user_email: str
    def __init__(self, google_uid: _Optional[str] = ..., user_email: _Optional[str] = ...) -> None: ...

class CreateTokenForGoogleUIDResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ("user_id", "include_user_details", "include_orgs")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_USER_DETAILS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ORGS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    include_user_details: bool
    include_orgs: bool
    def __init__(self, user_id: _Optional[str] = ..., include_user_details: bool = ..., include_orgs: bool = ...) -> None: ...

class GetUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class ResolveUserNameRequest(_message.Message):
    __slots__ = ("user_name", "include_orgs")
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ORGS_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    include_orgs: bool
    def __init__(self, user_name: _Optional[str] = ..., include_orgs: bool = ...) -> None: ...

class ResolveUserNameResponse(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class ListUsersRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "include_user_details")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        INCLUDE_USER_DETAILS_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListUsersRequest.Opts.SortClause
        page_size: int
        organization_id: str
        include_user_details: bool
        def __init__(self, sort_clause: _Optional[_Union[ListUsersRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., include_user_details: bool = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListUsersRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListUsersRequest.Opts, _Mapping]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("name", "email", "google_uid", "report_group")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_UID_FIELD_NUMBER: _ClassVar[int]
    REPORT_GROUP_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    google_uid: str
    report_group: str
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., google_uid: _Optional[str] = ..., report_group: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("user_id", "name", "display_name", "pronouns", "email", "role")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PRONOUNS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    display_name: str
    pronouns: str
    email: str
    role: AuthRole
    def __init__(self, user_id: _Optional[str] = ..., name: _Optional[str] = ..., display_name: _Optional[str] = ..., pronouns: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[_Union[AuthRole, str]] = ...) -> None: ...

class UpdateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class ListUsersResponse(_message.Message):
    __slots__ = ("next_page_token", "users")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, next_page_token: _Optional[str] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class RegenerateUserAuthTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegenerateUserAuthTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class GetOrganizationRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class GetOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: Organization
    def __init__(self, organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class ResolveOrganizationNameRequest(_message.Message):
    __slots__ = ("organization_name",)
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    organization_name: str
    def __init__(self, organization_name: _Optional[str] = ...) -> None: ...

class ResolveOrganizationNameResponse(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class ListOrganizationsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "member_user_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        MEMBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListOrganizationsRequest.Opts.SortClause
        page_size: int
        member_user_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListOrganizationsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., member_user_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListOrganizationsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListOrganizationsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListOrganizationsResponse(_message.Message):
    __slots__ = ("next_page_token", "organizations")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    organizations: _containers.RepeatedCompositeFieldContainer[Organization]
    def __init__(self, next_page_token: _Optional[str] = ..., organizations: _Optional[_Iterable[_Union[Organization, _Mapping]]] = ...) -> None: ...

class GetWorkspaceRequest(_message.Message):
    __slots__ = ("workspace_id",)
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class GetWorkspaceResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class ResolveWorkspaceNameRequest(_message.Message):
    __slots__ = ("owner_name", "workspace_name")
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    owner_name: str
    workspace_name: str
    def __init__(self, owner_name: _Optional[str] = ..., workspace_name: _Optional[str] = ...) -> None: ...

class ResolveWorkspaceNameResponse(_message.Message):
    __slots__ = ("workspace_id",)
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class ListWorkspacesRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "author_id", "only_archived", "include_workspace_size", "workload_author_id", "name_or_description_substring")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name", "recent_workload_activity", "maximum_workload_priority")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            RECENT_WORKLOAD_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
            MAXIMUM_WORKLOAD_PRIORITY_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            recent_workload_activity: _empty_pb2.Empty
            maximum_workload_priority: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., recent_workload_activity: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., maximum_workload_priority: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        ONLY_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
        INCLUDE_WORKSPACE_SIZE_FIELD_NUMBER: _ClassVar[int]
        WORKLOAD_AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_OR_DESCRIPTION_SUBSTRING_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListWorkspacesRequest.Opts.SortClause
        page_size: int
        organization_id: str
        author_id: str
        only_archived: bool
        include_workspace_size: bool
        workload_author_id: str
        name_or_description_substring: str
        def __init__(self, sort_clause: _Optional[_Union[ListWorkspacesRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., author_id: _Optional[str] = ..., only_archived: bool = ..., include_workspace_size: bool = ..., workload_author_id: _Optional[str] = ..., name_or_description_substring: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListWorkspacesRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListWorkspacesRequest.Opts, _Mapping]] = ...) -> None: ...

class ListWorkspacesResponse(_message.Message):
    __slots__ = ("next_page_token", "workspaces")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKSPACES_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    workspaces: _containers.RepeatedCompositeFieldContainer[Workspace]
    def __init__(self, next_page_token: _Optional[str] = ..., workspaces: _Optional[_Iterable[_Union[Workspace, _Mapping]]] = ...) -> None: ...

class CreateWorkspaceRequest(_message.Message):
    __slots__ = ("name", "organization_id", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    organization_id: str
    description: str
    def __init__(self, name: _Optional[str] = ..., organization_id: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class CreateWorkspaceResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class UpdateWorkspaceRequest(_message.Message):
    __slots__ = ("workspace_id", "name", "description", "archived", "maximum_workspace_priority", "budget_id")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_WORKSPACE_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    name: str
    description: str
    archived: bool
    maximum_workspace_priority: JobPriority
    budget_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., archived: bool = ..., maximum_workspace_priority: _Optional[_Union[JobPriority, str]] = ..., budget_id: _Optional[str] = ...) -> None: ...

class UpdateWorkspaceResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class TransferIntoWorkspaceRequest(_message.Message):
    __slots__ = ("workspace_id", "entity_ids")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_IDS_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    entity_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workspace_id: _Optional[str] = ..., entity_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class TransferIntoWorkspaceResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class UpdateWorkspaceSlotLimitNonPreemptibleRequest(_message.Message):
    __slots__ = ("workspace_id", "slot_limit_non_preemptible")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_LIMIT_NON_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    slot_limit_non_preemptible: int
    def __init__(self, workspace_id: _Optional[str] = ..., slot_limit_non_preemptible: _Optional[int] = ...) -> None: ...

class UpdateWorkspaceSlotLimitNonPreemptibleResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class UpdateWorkspaceSlotLimitPreemptibleRequest(_message.Message):
    __slots__ = ("workspace_id", "slot_limit_preemptible")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_LIMIT_PREEMPTIBLE_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    slot_limit_preemptible: int
    def __init__(self, workspace_id: _Optional[str] = ..., slot_limit_preemptible: _Optional[int] = ...) -> None: ...

class UpdateWorkspaceSlotLimitPreemptibleResponse(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: Workspace
    def __init__(self, workspace: _Optional[_Union[Workspace, _Mapping]] = ...) -> None: ...

class GetClusterRequest(_message.Message):
    __slots__ = ("cluster_id", "include_cluster_occupancy")
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_CLUSTER_OCCUPANCY_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    include_cluster_occupancy: bool
    def __init__(self, cluster_id: _Optional[str] = ..., include_cluster_occupancy: bool = ...) -> None: ...

class GetClusterResponse(_message.Message):
    __slots__ = ("cluster",)
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    cluster: Cluster
    def __init__(self, cluster: _Optional[_Union[Cluster, _Mapping]] = ...) -> None: ...

class ResolveClusterNameRequest(_message.Message):
    __slots__ = ("owner_name", "cluster_name")
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    owner_name: str
    cluster_name: str
    def __init__(self, owner_name: _Optional[str] = ..., cluster_name: _Optional[str] = ...) -> None: ...

class ResolveClusterNameResponse(_message.Message):
    __slots__ = ("cluster_id",)
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class ListClustersRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "include_deleted", "include_cluster_occupancy")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name", "running_jobs", "total_nodes", "free_gpus", "total_gpus")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            RUNNING_JOBS_FIELD_NUMBER: _ClassVar[int]
            TOTAL_NODES_FIELD_NUMBER: _ClassVar[int]
            FREE_GPUS_FIELD_NUMBER: _ClassVar[int]
            TOTAL_GPUS_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            running_jobs: _empty_pb2.Empty
            total_nodes: _empty_pb2.Empty
            free_gpus: _empty_pb2.Empty
            total_gpus: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., running_jobs: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., total_nodes: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., free_gpus: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., total_gpus: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        INCLUDE_DELETED_FIELD_NUMBER: _ClassVar[int]
        INCLUDE_CLUSTER_OCCUPANCY_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListClustersRequest.Opts.SortClause
        page_size: int
        organization_id: str
        include_deleted: bool
        include_cluster_occupancy: bool
        def __init__(self, sort_clause: _Optional[_Union[ListClustersRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., include_deleted: bool = ..., include_cluster_occupancy: bool = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListClustersRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListClustersRequest.Opts, _Mapping]] = ...) -> None: ...

class ListClustersResponse(_message.Message):
    __slots__ = ("next_page_token", "clusters")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    clusters: _containers.RepeatedCompositeFieldContainer[Cluster]
    def __init__(self, next_page_token: _Optional[str] = ..., clusters: _Optional[_Iterable[_Union[Cluster, _Mapping]]] = ...) -> None: ...

class UpdateClusterRequest(_message.Message):
    __slots__ = ("cluster_id", "max_session_timeout", "no_max_session_timeout", "max_task_timeout", "no_max_task_timeout", "allow_preemptible_restriction_exception", "require_preemptible_tasks", "restricted_user_ids", "clear_restricted_user_ids", "scheduling_policy")
    class RestrictedUserIds(_message.Message):
        __slots__ = ("restricted_user_ids",)
        RESTRICTED_USER_IDS_FIELD_NUMBER: _ClassVar[int]
        restricted_user_ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, restricted_user_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_SESSION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    NO_MAX_SESSION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_TASK_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    NO_MAX_TASK_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PREEMPTIBLE_RESTRICTION_EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_PREEMPTIBLE_TASKS_FIELD_NUMBER: _ClassVar[int]
    RESTRICTED_USER_IDS_FIELD_NUMBER: _ClassVar[int]
    CLEAR_RESTRICTED_USER_IDS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULING_POLICY_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    max_session_timeout: _duration_pb2.Duration
    no_max_session_timeout: _empty_pb2.Empty
    max_task_timeout: _duration_pb2.Duration
    no_max_task_timeout: _empty_pb2.Empty
    allow_preemptible_restriction_exception: bool
    require_preemptible_tasks: bool
    restricted_user_ids: UpdateClusterRequest.RestrictedUserIds
    clear_restricted_user_ids: _empty_pb2.Empty
    scheduling_policy: ClusterSchedulingPolicy
    def __init__(self, cluster_id: _Optional[str] = ..., max_session_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., no_max_session_timeout: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., max_task_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., no_max_task_timeout: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., allow_preemptible_restriction_exception: bool = ..., require_preemptible_tasks: bool = ..., restricted_user_ids: _Optional[_Union[UpdateClusterRequest.RestrictedUserIds, _Mapping]] = ..., clear_restricted_user_ids: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., scheduling_policy: _Optional[_Union[ClusterSchedulingPolicy, str]] = ...) -> None: ...

class UpdateClusterResponse(_message.Message):
    __slots__ = ("cluster",)
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    cluster: Cluster
    def __init__(self, cluster: _Optional[_Union[Cluster, _Mapping]] = ...) -> None: ...

class ListClusterSlotUsageRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "cluster_id", "instant", "range")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "usage")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            USAGE_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            usage: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., usage: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        INSTANT_FIELD_NUMBER: _ClassVar[int]
        RANGE_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListClusterSlotUsageRequest.Opts.SortClause
        page_size: int
        cluster_id: str
        instant: _timestamp_pb2.Timestamp
        range: Interval
        def __init__(self, sort_clause: _Optional[_Union[ListClusterSlotUsageRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., cluster_id: _Optional[str] = ..., instant: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., range: _Optional[_Union[Interval, _Mapping]] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListClusterSlotUsageRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListClusterSlotUsageRequest.Opts, _Mapping]] = ...) -> None: ...

class ListClusterSlotUsageResponse(_message.Message):
    __slots__ = ("next_page_token", "cluster_slot_usages")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_SLOT_USAGES_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    cluster_slot_usages: _containers.RepeatedCompositeFieldContainer[ClusterSlotUsage]
    def __init__(self, next_page_token: _Optional[str] = ..., cluster_slot_usages: _Optional[_Iterable[_Union[ClusterSlotUsage, _Mapping]]] = ...) -> None: ...

class GetNodeRequest(_message.Message):
    __slots__ = ("node_id",)
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    def __init__(self, node_id: _Optional[str] = ...) -> None: ...

class GetNodeResponse(_message.Message):
    __slots__ = ("node",)
    NODE_FIELD_NUMBER: _ClassVar[int]
    node: Node
    def __init__(self, node: _Optional[_Union[Node, _Mapping]] = ...) -> None: ...

class ListNodesRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "cluster_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name", "recent_activity_for_user_id", "utilization")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            RECENT_ACTIVITY_FOR_USER_ID_FIELD_NUMBER: _ClassVar[int]
            UTILIZATION_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            recent_activity_for_user_id: str
            utilization: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., recent_activity_for_user_id: _Optional[str] = ..., utilization: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListNodesRequest.Opts.SortClause
        page_size: int
        organization_id: str
        cluster_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListNodesRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., cluster_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListNodesRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListNodesRequest.Opts, _Mapping]] = ...) -> None: ...

class ListNodesResponse(_message.Message):
    __slots__ = ("next_page_token", "nodes")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, next_page_token: _Optional[str] = ..., nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class CordonNodeRequest(_message.Message):
    __slots__ = ("node_id", "cordon_reason", "desired_state")
    class DesiredState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DESIRED_STATE_UNSPECIFIED: _ClassVar[CordonNodeRequest.DesiredState]
        DESIRED_STATE_CORDONED: _ClassVar[CordonNodeRequest.DesiredState]
        DESIRED_STATE_NOT_CORDONED: _ClassVar[CordonNodeRequest.DesiredState]
    DESIRED_STATE_UNSPECIFIED: CordonNodeRequest.DesiredState
    DESIRED_STATE_CORDONED: CordonNodeRequest.DesiredState
    DESIRED_STATE_NOT_CORDONED: CordonNodeRequest.DesiredState
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    CORDON_REASON_FIELD_NUMBER: _ClassVar[int]
    DESIRED_STATE_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    cordon_reason: str
    desired_state: CordonNodeRequest.DesiredState
    def __init__(self, node_id: _Optional[str] = ..., cordon_reason: _Optional[str] = ..., desired_state: _Optional[_Union[CordonNodeRequest.DesiredState, str]] = ...) -> None: ...

class CordonNodeResponse(_message.Message):
    __slots__ = ("node",)
    NODE_FIELD_NUMBER: _ClassVar[int]
    node: Node
    def __init__(self, node: _Optional[_Union[Node, _Mapping]] = ...) -> None: ...

class ExpireNodeRequest(_message.Message):
    __slots__ = ("node_id",)
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    def __init__(self, node_id: _Optional[str] = ...) -> None: ...

class GetWorkloadRequest(_message.Message):
    __slots__ = ("workload_id",)
    WORKLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    workload_id: str
    def __init__(self, workload_id: _Optional[str] = ...) -> None: ...

class GetWorkloadResponse(_message.Message):
    __slots__ = ("workload",)
    WORKLOAD_FIELD_NUMBER: _ClassVar[int]
    workload: Workload
    def __init__(self, workload: _Optional[_Union[Workload, _Mapping]] = ...) -> None: ...

class ResolveWorkloadNameRequest(_message.Message):
    __slots__ = ("author_name", "workload_name")
    AUTHOR_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKLOAD_NAME_FIELD_NUMBER: _ClassVar[int]
    author_name: str
    workload_name: str
    def __init__(self, author_name: _Optional[str] = ..., workload_name: _Optional[str] = ...) -> None: ...

class ResolveWorkloadNameResponse(_message.Message):
    __slots__ = ("workload_id",)
    WORKLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    workload_id: str
    def __init__(self, workload_id: _Optional[str] = ...) -> None: ...

class ListWorkloadsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "workspace_id", "workload_type", "author_id", "statuses", "job_finalized", "name_or_description_substring", "created_before", "created_after")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
        WORKLOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        STATUSES_FIELD_NUMBER: _ClassVar[int]
        JOB_FINALIZED_FIELD_NUMBER: _ClassVar[int]
        NAME_OR_DESCRIPTION_SUBSTRING_FIELD_NUMBER: _ClassVar[int]
        CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListWorkloadsRequest.Opts.SortClause
        page_size: int
        organization_id: str
        workspace_id: str
        workload_type: WorkloadType
        author_id: str
        statuses: _containers.RepeatedScalarFieldContainer[WorkloadStatus]
        job_finalized: bool
        name_or_description_substring: str
        created_before: _timestamp_pb2.Timestamp
        created_after: _timestamp_pb2.Timestamp
        def __init__(self, sort_clause: _Optional[_Union[ListWorkloadsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., workload_type: _Optional[_Union[WorkloadType, str]] = ..., author_id: _Optional[str] = ..., statuses: _Optional[_Iterable[_Union[WorkloadStatus, str]]] = ..., job_finalized: bool = ..., name_or_description_substring: _Optional[str] = ..., created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListWorkloadsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListWorkloadsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListWorkloadsResponse(_message.Message):
    __slots__ = ("next_page_token", "workloads")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKLOADS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    workloads: _containers.RepeatedCompositeFieldContainer[Workload]
    def __init__(self, next_page_token: _Optional[str] = ..., workloads: _Optional[_Iterable[_Union[Workload, _Mapping]]] = ...) -> None: ...

class UpdateWorkloadRequest(_message.Message):
    __slots__ = ("workload_id", "name", "description")
    WORKLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    workload_id: str
    name: str
    description: str
    def __init__(self, workload_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateWorkloadResponse(_message.Message):
    __slots__ = ("workload",)
    WORKLOAD_FIELD_NUMBER: _ClassVar[int]
    workload: Workload
    def __init__(self, workload: _Optional[_Union[Workload, _Mapping]] = ...) -> None: ...

class CancelWorkloadsRequest(_message.Message):
    __slots__ = ("workload_ids",)
    WORKLOAD_IDS_FIELD_NUMBER: _ClassVar[int]
    workload_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workload_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CancelWorkloadsResponse(_message.Message):
    __slots__ = ("workload_ids",)
    WORKLOAD_IDS_FIELD_NUMBER: _ClassVar[int]
    workload_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workload_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteWorkloadsRequest(_message.Message):
    __slots__ = ("workload_ids",)
    WORKLOAD_IDS_FIELD_NUMBER: _ClassVar[int]
    workload_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workload_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteWorkloadsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "task_id", "environment_id", "finalized", "eligible_for_cluster_id", "scheduled_on_node_id", "scheduled_on_cluster_id", "scheduled", "retry_ancestors_of_non_scheduled_non_finalized_jobs")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "cluster_job_queue")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            CLUSTER_JOB_QUEUE_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            cluster_job_queue: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., cluster_job_queue: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
        FINALIZED_FIELD_NUMBER: _ClassVar[int]
        ELIGIBLE_FOR_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        SCHEDULED_ON_NODE_ID_FIELD_NUMBER: _ClassVar[int]
        SCHEDULED_ON_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        SCHEDULED_FIELD_NUMBER: _ClassVar[int]
        RETRY_ANCESTORS_OF_NON_SCHEDULED_NON_FINALIZED_JOBS_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListJobsRequest.Opts.SortClause
        page_size: int
        organization_id: str
        task_id: str
        environment_id: str
        finalized: bool
        eligible_for_cluster_id: str
        scheduled_on_node_id: str
        scheduled_on_cluster_id: str
        scheduled: bool
        retry_ancestors_of_non_scheduled_non_finalized_jobs: bool
        def __init__(self, sort_clause: _Optional[_Union[ListJobsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., task_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., finalized: bool = ..., eligible_for_cluster_id: _Optional[str] = ..., scheduled_on_node_id: _Optional[str] = ..., scheduled_on_cluster_id: _Optional[str] = ..., scheduled: bool = ..., retry_ancestors_of_non_scheduled_non_finalized_jobs: bool = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListJobsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListJobsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ("next_page_token", "jobs")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    jobs: _containers.RepeatedCompositeFieldContainer[Job]
    def __init__(self, next_page_token: _Optional[str] = ..., jobs: _Optional[_Iterable[_Union[Job, _Mapping]]] = ...) -> None: ...

class ScheduleJobsRequest(_message.Message):
    __slots__ = ("job_assignments", "job_cancelations", "job_reschedulings", "node_actions")
    JOB_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    JOB_CANCELATIONS_FIELD_NUMBER: _ClassVar[int]
    JOB_RESCHEDULINGS_FIELD_NUMBER: _ClassVar[int]
    NODE_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    job_assignments: _containers.RepeatedCompositeFieldContainer[JobAssignment]
    job_cancelations: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    job_reschedulings: _containers.RepeatedCompositeFieldContainer[JobCancelation]
    node_actions: _containers.RepeatedCompositeFieldContainer[NodeAction]
    def __init__(self, job_assignments: _Optional[_Iterable[_Union[JobAssignment, _Mapping]]] = ..., job_cancelations: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., job_reschedulings: _Optional[_Iterable[_Union[JobCancelation, _Mapping]]] = ..., node_actions: _Optional[_Iterable[_Union[NodeAction, _Mapping]]] = ...) -> None: ...

class NodeAction(_message.Message):
    __slots__ = ("cordon", "expire")
    CORDON_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_FIELD_NUMBER: _ClassVar[int]
    cordon: CordonNodeRequest
    expire: ExpireNodeRequest
    def __init__(self, cordon: _Optional[_Union[CordonNodeRequest, _Mapping]] = ..., expire: _Optional[_Union[ExpireNodeRequest, _Mapping]] = ...) -> None: ...

class ScheduleJobsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateJobSourcePriorityRequest(_message.Message):
    __slots__ = ("job_id", "priority")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    priority: JobPriority
    def __init__(self, job_id: _Optional[str] = ..., priority: _Optional[_Union[JobPriority, str]] = ...) -> None: ...

class UpdateJobSourcePriorityResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class PreemptJobRequest(_message.Message):
    __slots__ = ("job_id", "canceled_for", "canceled_code")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FOR_FIELD_NUMBER: _ClassVar[int]
    CANCELED_CODE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    canceled_for: str
    canceled_code: CancelationCode
    def __init__(self, job_id: _Optional[str] = ..., canceled_for: _Optional[str] = ..., canceled_code: _Optional[_Union[CancelationCode, str]] = ...) -> None: ...

class PreemptJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class RescheduleJobRequest(_message.Message):
    __slots__ = ("job_id", "canceled_for", "canceled_code")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FOR_FIELD_NUMBER: _ClassVar[int]
    CANCELED_CODE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    canceled_for: str
    canceled_code: CancelationCode
    def __init__(self, job_id: _Optional[str] = ..., canceled_for: _Optional[str] = ..., canceled_code: _Optional[_Union[CancelationCode, str]] = ...) -> None: ...

class RescheduleJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class StreamJobLogsRequest(_message.Message):
    __slots__ = ("job_id", "tail_lines", "follow", "since")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TAIL_LINES_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    SINCE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    tail_lines: int
    follow: bool
    since: _timestamp_pb2.Timestamp
    def __init__(self, job_id: _Optional[str] = ..., tail_lines: _Optional[int] = ..., follow: bool = ..., since: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateJobEventRequest(_message.Message):
    __slots__ = ("job_id", "status", "message", "occurred")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: str
    message: str
    occurred: _timestamp_pb2.Timestamp
    def __init__(self, job_id: _Optional[str] = ..., status: _Optional[str] = ..., message: _Optional[str] = ..., occurred: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateJobEventsRequest(_message.Message):
    __slots__ = ("job_events",)
    JOB_EVENTS_FIELD_NUMBER: _ClassVar[int]
    job_events: _containers.RepeatedCompositeFieldContainer[CreateJobEventRequest]
    def __init__(self, job_events: _Optional[_Iterable[_Union[CreateJobEventRequest, _Mapping]]] = ...) -> None: ...

class CreateJobEventsResponse(_message.Message):
    __slots__ = ("job_events",)
    JOB_EVENTS_FIELD_NUMBER: _ClassVar[int]
    job_events: _containers.RepeatedCompositeFieldContainer[JobEvent]
    def __init__(self, job_events: _Optional[_Iterable[_Union[JobEvent, _Mapping]]] = ...) -> None: ...

class ClusterJobQueue(_message.Message):
    __slots__ = ("cluster_id", "job_ids", "failed_scheduling_messages")
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    FAILED_SCHEDULING_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    failed_scheduling_messages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, cluster_id: _Optional[str] = ..., job_ids: _Optional[_Iterable[str]] = ..., failed_scheduling_messages: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateJobQueueRequest(_message.Message):
    __slots__ = ("organization_id", "cluster_job_queues")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_JOB_QUEUES_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    cluster_job_queues: _containers.RepeatedCompositeFieldContainer[ClusterJobQueue]
    def __init__(self, organization_id: _Optional[str] = ..., cluster_job_queues: _Optional[_Iterable[_Union[ClusterJobQueue, _Mapping]]] = ...) -> None: ...

class UpdateJobQueueResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSummarizedJobEventsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "job_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "latest_occurrence")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            LATEST_OCCURRENCE_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            latest_occurrence: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., latest_occurrence: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        JOB_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListSummarizedJobEventsRequest.Opts.SortClause
        page_size: int
        job_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListSummarizedJobEventsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., job_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListSummarizedJobEventsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListSummarizedJobEventsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListSummarizedJobEventsResponse(_message.Message):
    __slots__ = ("next_page_token", "summarized_job_events")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SUMMARIZED_JOB_EVENTS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    summarized_job_events: _containers.RepeatedCompositeFieldContainer[SummarizedJobEvent]
    def __init__(self, next_page_token: _Optional[str] = ..., summarized_job_events: _Optional[_Iterable[_Union[SummarizedJobEvent, _Mapping]]] = ...) -> None: ...

class GetExperimentYamlSpecRequest(_message.Message):
    __slots__ = ("experiment_id",)
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    def __init__(self, experiment_id: _Optional[str] = ...) -> None: ...

class GetExperimentYamlSpecResponse(_message.Message):
    __slots__ = ("experiment_spec",)
    EXPERIMENT_SPEC_FIELD_NUMBER: _ClassVar[int]
    experiment_spec: str
    def __init__(self, experiment_spec: _Optional[str] = ...) -> None: ...

class RestartExperimentTasksRequest(_message.Message):
    __slots__ = ("experiment_id",)
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    def __init__(self, experiment_id: _Optional[str] = ...) -> None: ...

class RestartExperimentTasksResponse(_message.Message):
    __slots__ = ("workload",)
    WORKLOAD_FIELD_NUMBER: _ClassVar[int]
    workload: Workload
    def __init__(self, workload: _Optional[_Union[Workload, _Mapping]] = ...) -> None: ...

class GetImageRequest(_message.Message):
    __slots__ = ("image_id",)
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    image_id: str
    def __init__(self, image_id: _Optional[str] = ...) -> None: ...

class GetImageResponse(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: Image
    def __init__(self, image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class ResolveImageNameRequest(_message.Message):
    __slots__ = ("author_name", "image_name")
    AUTHOR_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    author_name: str
    image_name: str
    def __init__(self, author_name: _Optional[str] = ..., image_name: _Optional[str] = ...) -> None: ...

class ResolveImageNameResponse(_message.Message):
    __slots__ = ("image_id",)
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    image_id: str
    def __init__(self, image_id: _Optional[str] = ...) -> None: ...

class ListImagesRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "image_name_or_description", "author_id", "workspace_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        IMAGE_NAME_OR_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListImagesRequest.Opts.SortClause
        page_size: int
        organization_id: str
        image_name_or_description: str
        author_id: str
        workspace_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListImagesRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., image_name_or_description: _Optional[str] = ..., author_id: _Optional[str] = ..., workspace_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListImagesRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListImagesRequest.Opts, _Mapping]] = ...) -> None: ...

class ListImagesResponse(_message.Message):
    __slots__ = ("next_page_token", "images")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    images: _containers.RepeatedCompositeFieldContainer[Image]
    def __init__(self, next_page_token: _Optional[str] = ..., images: _Optional[_Iterable[_Union[Image, _Mapping]]] = ...) -> None: ...

class UpdateImageRequest(_message.Message):
    __slots__ = ("image_id", "name", "description", "committed")
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_FIELD_NUMBER: _ClassVar[int]
    image_id: str
    name: str
    description: str
    committed: _empty_pb2.Empty
    def __init__(self, image_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., committed: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class UpdateImageResponse(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: Image
    def __init__(self, image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class DeleteImagesRequest(_message.Message):
    __slots__ = ("image_ids",)
    IMAGE_IDS_FIELD_NUMBER: _ClassVar[int]
    image_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, image_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteImagesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSecretRequest(_message.Message):
    __slots__ = ("workspace_id", "secret_name")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    secret_name: str
    def __init__(self, workspace_id: _Optional[str] = ..., secret_name: _Optional[str] = ...) -> None: ...

class GetSecretResponse(_message.Message):
    __slots__ = ("secret",)
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: Secret
    def __init__(self, secret: _Optional[_Union[Secret, _Mapping]] = ...) -> None: ...

class ListSecretsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "workspace_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListSecretsRequest.Opts.SortClause
        page_size: int
        workspace_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListSecretsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., workspace_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListSecretsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListSecretsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListSecretsResponse(_message.Message):
    __slots__ = ("next_page_token", "secrets")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    secrets: _containers.RepeatedCompositeFieldContainer[Secret]
    def __init__(self, next_page_token: _Optional[str] = ..., secrets: _Optional[_Iterable[_Union[Secret, _Mapping]]] = ...) -> None: ...

class ListGroupsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "workspace_id", "name_or_description_substring", "author_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "modified", "name")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            MODIFIED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            modified: _empty_pb2.Empty
            name: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., modified: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_OR_DESCRIPTION_SUBSTRING_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListGroupsRequest.Opts.SortClause
        page_size: int
        organization_id: str
        workspace_id: str
        name_or_description_substring: str
        author_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListGroupsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., name_or_description_substring: _Optional[str] = ..., author_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListGroupsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListGroupsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListGroupsResponse(_message.Message):
    __slots__ = ("next_page_token", "groups")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    groups: _containers.RepeatedCompositeFieldContainer[Group]
    def __init__(self, next_page_token: _Optional[str] = ..., groups: _Optional[_Iterable[_Union[Group, _Mapping]]] = ...) -> None: ...

class GetGroupRequest(_message.Message):
    __slots__ = ("group_id",)
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    def __init__(self, group_id: _Optional[str] = ...) -> None: ...

class GetGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: Group
    def __init__(self, group: _Optional[_Union[Group, _Mapping]] = ...) -> None: ...

class UpdateGroupRequest(_message.Message):
    __slots__ = ("group_id", "set_parameters", "archived", "name", "description", "add_experiment_ids")
    class SetParameters(_message.Message):
        __slots__ = ("parameters",)
        PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        parameters: _containers.RepeatedCompositeFieldContainer[GroupParameter]
        def __init__(self, parameters: _Optional[_Iterable[_Union[GroupParameter, _Mapping]]] = ...) -> None: ...
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SET_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ADD_EXPERIMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    set_parameters: UpdateGroupRequest.SetParameters
    archived: bool
    name: str
    description: str
    add_experiment_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, group_id: _Optional[str] = ..., set_parameters: _Optional[_Union[UpdateGroupRequest.SetParameters, _Mapping]] = ..., archived: bool = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., add_experiment_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: Group
    def __init__(self, group: _Optional[_Union[Group, _Mapping]] = ...) -> None: ...

class CreateGroupRequest(_message.Message):
    __slots__ = ("workspace_id", "name", "description", "experiment_ids")
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    name: str
    description: str
    experiment_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workspace_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., experiment_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: Group
    def __init__(self, group: _Optional[_Union[Group, _Mapping]] = ...) -> None: ...

class ListGroupTaskMetricsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "group_id")
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "experiment_name", "task_name", "group_parameter")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
            TASK_NAME_FIELD_NUMBER: _ClassVar[int]
            GROUP_PARAMETER_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            experiment_name: _empty_pb2.Empty
            task_name: _empty_pb2.Empty
            group_parameter: GroupParameter
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., experiment_name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., task_name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., group_parameter: _Optional[_Union[GroupParameter, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListGroupTaskMetricsRequest.Opts.SortClause
        page_size: int
        group_id: str
        def __init__(self, sort_clause: _Optional[_Union[ListGroupTaskMetricsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., group_id: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListGroupTaskMetricsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListGroupTaskMetricsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListGroupTaskMetricsResponse(_message.Message):
    __slots__ = ("next_page_token", "task_metrics")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TASK_METRICS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    task_metrics: _containers.RepeatedCompositeFieldContainer[TaskMetrics]
    def __init__(self, next_page_token: _Optional[str] = ..., task_metrics: _Optional[_Iterable[_Union[TaskMetrics, _Mapping]]] = ...) -> None: ...

class GetGroupMetricsExportRequest(_message.Message):
    __slots__ = ("group_id",)
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    def __init__(self, group_id: _Optional[str] = ...) -> None: ...

class GetGroupMetricsExportResponse(_message.Message):
    __slots__ = ("csv_data",)
    CSV_DATA_FIELD_NUMBER: _ClassVar[int]
    csv_data: str
    def __init__(self, csv_data: _Optional[str] = ...) -> None: ...

class DeleteGroupsRequest(_message.Message):
    __slots__ = ("group_ids",)
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    group_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, group_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteGroupsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetDatasetRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class GetDatasetResponse(_message.Message):
    __slots__ = ("dataset", "datasetStorage")
    DATASET_FIELD_NUMBER: _ClassVar[int]
    DATASETSTORAGE_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    datasetStorage: DatasetStorage
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ..., datasetStorage: _Optional[_Union[DatasetStorage, _Mapping]] = ...) -> None: ...

class ListDatasetsRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("sort_clause", "page_size", "organization_id", "workspace_id", "author_id", "name_or_description_substring", "created_before", "created_after", "dataset_type", "committed_status")
        class DatasetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DATASET_TYPE_UNSPECIFIED: _ClassVar[ListDatasetsRequest.Opts.DatasetType]
            DATASET_TYPE_IS_NOT_RESULT: _ClassVar[ListDatasetsRequest.Opts.DatasetType]
            DATASET_TYPE_IS_RESULT: _ClassVar[ListDatasetsRequest.Opts.DatasetType]
        DATASET_TYPE_UNSPECIFIED: ListDatasetsRequest.Opts.DatasetType
        DATASET_TYPE_IS_NOT_RESULT: ListDatasetsRequest.Opts.DatasetType
        DATASET_TYPE_IS_RESULT: ListDatasetsRequest.Opts.DatasetType
        class CommittedStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            STATUS_UNSPECIFIED: _ClassVar[ListDatasetsRequest.Opts.CommittedStatus]
            STATUS_COMMITTED: _ClassVar[ListDatasetsRequest.Opts.CommittedStatus]
            STATUS_UNCOMMITTED: _ClassVar[ListDatasetsRequest.Opts.CommittedStatus]
        STATUS_UNSPECIFIED: ListDatasetsRequest.Opts.CommittedStatus
        STATUS_COMMITTED: ListDatasetsRequest.Opts.CommittedStatus
        STATUS_UNCOMMITTED: ListDatasetsRequest.Opts.CommittedStatus
        class SortClause(_message.Message):
            __slots__ = ("sort_order", "created", "name")
            SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
            CREATED_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            sort_order: SortOrder
            created: _empty_pb2.Empty
            name: _empty_pb2.Empty
            def __init__(self, sort_order: _Optional[_Union[SortOrder, str]] = ..., created: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., name: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
        SORT_CLAUSE_FIELD_NUMBER: _ClassVar[int]
        PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_OR_DESCRIPTION_SUBSTRING_FIELD_NUMBER: _ClassVar[int]
        CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
        DATASET_TYPE_FIELD_NUMBER: _ClassVar[int]
        COMMITTED_STATUS_FIELD_NUMBER: _ClassVar[int]
        sort_clause: ListDatasetsRequest.Opts.SortClause
        page_size: int
        organization_id: str
        workspace_id: str
        author_id: str
        name_or_description_substring: str
        created_before: _timestamp_pb2.Timestamp
        created_after: _timestamp_pb2.Timestamp
        dataset_type: ListDatasetsRequest.Opts.DatasetType
        committed_status: ListDatasetsRequest.Opts.CommittedStatus
        def __init__(self, sort_clause: _Optional[_Union[ListDatasetsRequest.Opts.SortClause, _Mapping]] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., author_id: _Optional[str] = ..., name_or_description_substring: _Optional[str] = ..., created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., dataset_type: _Optional[_Union[ListDatasetsRequest.Opts.DatasetType, str]] = ..., committed_status: _Optional[_Union[ListDatasetsRequest.Opts.CommittedStatus, str]] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListDatasetsRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListDatasetsRequest.Opts, _Mapping]] = ...) -> None: ...

class ListDatasetsResponse(_message.Message):
    __slots__ = ("next_page_token", "datasets")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    datasets: _containers.RepeatedCompositeFieldContainer[Dataset]
    def __init__(self, next_page_token: _Optional[str] = ..., datasets: _Optional[_Iterable[_Union[Dataset, _Mapping]]] = ...) -> None: ...

class UpdateDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "name", "description", "committed")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    name: str
    description: str
    committed: _empty_pb2.Empty
    def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., committed: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class UpdateDatasetResponse(_message.Message):
    __slots__ = ("dataset", "datasetStorage")
    DATASET_FIELD_NUMBER: _ClassVar[int]
    DATASETSTORAGE_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    datasetStorage: DatasetStorage
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ..., datasetStorage: _Optional[_Union[DatasetStorage, _Mapping]] = ...) -> None: ...

class ListDatasetFilesRequest(_message.Message):
    __slots__ = ("next_page_token", "options")
    class Opts(_message.Message):
        __slots__ = ("dataset_id", "prefix")
        DATASET_ID_FIELD_NUMBER: _ClassVar[int]
        PREFIX_FIELD_NUMBER: _ClassVar[int]
        dataset_id: str
        prefix: str
        def __init__(self, dataset_id: _Optional[str] = ..., prefix: _Optional[str] = ...) -> None: ...
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    options: ListDatasetFilesRequest.Opts
    def __init__(self, next_page_token: _Optional[str] = ..., options: _Optional[_Union[ListDatasetFilesRequest.Opts, _Mapping]] = ...) -> None: ...

class ListDatasetFilesResponse(_message.Message):
    __slots__ = ("next_page_token", "dataset_files", "total_size", "file_count")
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATASET_FILES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    FILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    next_page_token: str
    dataset_files: _containers.RepeatedCompositeFieldContainer[DatasetFile]
    total_size: int
    file_count: int
    def __init__(self, next_page_token: _Optional[str] = ..., dataset_files: _Optional[_Iterable[_Union[DatasetFile, _Mapping]]] = ..., total_size: _Optional[int] = ..., file_count: _Optional[int] = ...) -> None: ...

class GetDatasetFileLinkRequest(_message.Message):
    __slots__ = ("dataset_id", "file_path")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    file_path: str
    def __init__(self, dataset_id: _Optional[str] = ..., file_path: _Optional[str] = ...) -> None: ...

class GetDatasetFileLinkResponse(_message.Message):
    __slots__ = ("download_url",)
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    download_url: str
    def __init__(self, download_url: _Optional[str] = ...) -> None: ...

class DeleteDatasetsRequest(_message.Message):
    __slots__ = ("dataset_ids",)
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    dataset_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dataset_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteDatasetsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSchedulerRunRequest(_message.Message):
    __slots__ = ("scheduler_run_id",)
    SCHEDULER_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    scheduler_run_id: str
    def __init__(self, scheduler_run_id: _Optional[str] = ...) -> None: ...

class GetSchedulerRunResponse(_message.Message):
    __slots__ = ("scheduler_run",)
    SCHEDULER_RUN_FIELD_NUMBER: _ClassVar[int]
    scheduler_run: SchedulerRun
    def __init__(self, scheduler_run: _Optional[_Union[SchedulerRun, _Mapping]] = ...) -> None: ...

class GetGPUUsageByBudgetRequest(_message.Message):
    __slots__ = ("org_id", "start", "end")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, org_id: _Optional[str] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GPUUsageByBudgetInterval(_message.Message):
    __slots__ = ("start", "end", "values")
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    values: _containers.ScalarMap[str, float]
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., values: _Optional[_Mapping[str, float]] = ...) -> None: ...

class GetGPUUsageByBudgetResponse(_message.Message):
    __slots__ = ("intervals",)
    INTERVALS_FIELD_NUMBER: _ClassVar[int]
    intervals: _containers.RepeatedCompositeFieldContainer[GPUUsageByBudgetInterval]
    def __init__(self, intervals: _Optional[_Iterable[_Union[GPUUsageByBudgetInterval, _Mapping]]] = ...) -> None: ...

class Healthcheck(_message.Message):
    __slots__ = ("id", "beaker_id", "docker_reference", "job", "started", "exited", "failed", "exit_code", "log", "failed_text")
    ID_FIELD_NUMBER: _ClassVar[int]
    BEAKER_ID_FIELD_NUMBER: _ClassVar[int]
    DOCKER_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    EXITED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    FAILED_TEXT_FIELD_NUMBER: _ClassVar[int]
    id: str
    beaker_id: str
    docker_reference: str
    job: str
    started: _timestamp_pb2.Timestamp
    exited: _timestamp_pb2.Timestamp
    failed: _timestamp_pb2.Timestamp
    exit_code: int
    log: str
    failed_text: str
    def __init__(self, id: _Optional[str] = ..., beaker_id: _Optional[str] = ..., docker_reference: _Optional[str] = ..., job: _Optional[str] = ..., started: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exited: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., failed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exit_code: _Optional[int] = ..., log: _Optional[str] = ..., failed_text: _Optional[str] = ...) -> None: ...

class CreateHealthcheckRequest(_message.Message):
    __slots__ = ("beaker_id", "docker_reference", "job", "started", "exited", "failed", "exit_code", "log", "failed_text")
    BEAKER_ID_FIELD_NUMBER: _ClassVar[int]
    DOCKER_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    EXITED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    FAILED_TEXT_FIELD_NUMBER: _ClassVar[int]
    beaker_id: str
    docker_reference: str
    job: str
    started: _timestamp_pb2.Timestamp
    exited: _timestamp_pb2.Timestamp
    failed: _timestamp_pb2.Timestamp
    exit_code: int
    log: str
    failed_text: str
    def __init__(self, beaker_id: _Optional[str] = ..., docker_reference: _Optional[str] = ..., job: _Optional[str] = ..., started: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exited: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., failed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., exit_code: _Optional[int] = ..., log: _Optional[str] = ..., failed_text: _Optional[str] = ...) -> None: ...

class CreateHealthcheckResponse(_message.Message):
    __slots__ = ("healthcheck",)
    HEALTHCHECK_FIELD_NUMBER: _ClassVar[int]
    healthcheck: Healthcheck
    def __init__(self, healthcheck: _Optional[_Union[Healthcheck, _Mapping]] = ...) -> None: ...

class GetBudgetRequest(_message.Message):
    __slots__ = ("budget_id",)
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    budget_id: str
    def __init__(self, budget_id: _Optional[str] = ...) -> None: ...

class GetBudgetResponse(_message.Message):
    __slots__ = ("budget",)
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    budget: Budget
    def __init__(self, budget: _Optional[_Union[Budget, _Mapping]] = ...) -> None: ...

class ResolveBudgetNameRequest(_message.Message):
    __slots__ = ("organization_name", "budget_name")
    ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    BUDGET_NAME_FIELD_NUMBER: _ClassVar[int]
    organization_name: str
    budget_name: str
    def __init__(self, organization_name: _Optional[str] = ..., budget_name: _Optional[str] = ...) -> None: ...

class ResolveBudgetNameResponse(_message.Message):
    __slots__ = ("budget_id",)
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    budget_id: str
    def __init__(self, budget_id: _Optional[str] = ...) -> None: ...
