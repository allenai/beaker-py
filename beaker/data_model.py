import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel as _BaseModel
from pydantic import Field, ValidationError, root_validator, validator

from .util import to_lower_camel

T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseModel(_BaseModel):
    class Config:
        validate_assignment = True
        alias_generator = to_lower_camel
        #  extra = "forbid"

    @root_validator(pre=True)
    def _rename_to_alias(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Required since Pydantic only allows to instantiate a model using field aliases.
        """
        return {to_lower_camel(k): v for k, v in values.items()}

    def __getitem__(self, key):
        try:
            return self.dict()[key]
        except KeyError:
            if not key.islower():
                snake_case_key = ""
                for c in key:
                    if c.isupper():
                        snake_case_key += "_"
                    snake_case_key += c.lower()
                try:
                    return self.dict()[snake_case_key]
                except KeyError:
                    pass
            raise

    @classmethod
    def from_json(cls: Type[T], json_data: Dict[str, Any]) -> T:
        try:
            return cls(**json_data)
        except ValidationError:
            logger.error("Error validating raw JSON data for %s: %s", cls.__name__, json_data)
            raise

    def to_json(self) -> Dict[str, Any]:
        return self.dict(by_alias=True, exclude_none=True)


class WorkspaceSize(BaseModel):
    datasets: int
    experiments: int
    groups: int
    images: int


class Account(BaseModel):
    id: str
    name: str
    display_name: str
    institution: Optional[str] = None


class Organization(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    display_name: str


class OrganizationMember(BaseModel):
    role: str
    organization: Organization
    user: Account


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


class Node(BaseModel):
    id: str
    hostname: str
    created: datetime
    expiry: datetime
    limits: NodeSpec


class Workspace(BaseModel):
    id: str
    name: str
    size: WorkspaceSize
    owner: Account
    author: Account
    created: datetime
    modified: datetime
    archived: bool = False
    full_name: str


class WorkspaceRef(BaseModel):
    id: str
    name: str
    full_name: str


class ExecutionState(BaseModel):
    created: Optional[datetime] = None
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    finalized: Optional[datetime] = None
    exit_code: Optional[int] = None

    @validator("created", "scheduled", "started", "exited", "finalized")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class JobStatus(BaseModel):
    created: Optional[datetime] = None
    scheduled: Optional[datetime] = None
    started: Optional[datetime] = None
    exited: Optional[datetime] = None
    finalized: Optional[datetime] = None
    exit_code: Optional[int] = None

    @validator("created", "scheduled", "started", "exited", "finalized")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class ExecutionResult(BaseModel):
    beaker: str


class ExecutionLimits(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpus: List[str] = Field(default_factory=list)


class Execution(BaseModel):
    id: str
    task: str
    experiment: str
    workspace: str
    author: Account
    spec: Dict[str, Any]
    result: ExecutionResult
    state: ExecutionState
    node: Optional[str] = None
    limits: Optional[ExecutionLimits] = None
    priority: str = "normal"


class JobRequests(BaseModel):
    gpu_count: Optional[int] = None
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    sharedMemory: Optional[str] = None


class JobLimits(BaseModel):
    cpu_count: Optional[float] = None
    memory: Optional[str] = None
    gpus: List[str] = Field(default_factory=list)


class JobExecution(BaseModel):
    task: str
    experiment: str
    workspace: str
    spec: Dict[str, Any]
    result: ExecutionResult


class Job(BaseModel):
    id: str
    kind: str
    name: str
    author: Account
    workspace: str
    cluster: str
    status: JobStatus
    execution: JobExecution
    node: Optional[str] = None
    requests: Optional[JobRequests] = None
    limits: Optional[JobLimits] = None


class Experiment(BaseModel):
    id: str
    name: str
    full_name: str
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    executions: List[Execution] = Field(default_factory=list)
    jobs: List[Job] = Field(default_factory=list)


class DatasetStorage(BaseModel):
    id: str
    address: str
    token: str
    token_expires: datetime


class DatasetSize(BaseModel):
    final: bool
    files: int
    bytes: int
    bytes_human: str


class Dataset(BaseModel):
    id: str
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    committed: Optional[datetime] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    storage: Optional[DatasetStorage] = None

    @validator("committed")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class DatasetStorageInfo(BaseModel):
    id: str
    created: Optional[datetime] = None
    size: Optional[DatasetSize] = None
    readonly: bool = True

    @validator("created")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class FileInfo(BaseModel):
    path: str
    size: int
    digest: str
    updated: datetime
    url: str


class DatasetManifest(BaseModel):
    files: List[FileInfo]
    cursor: Optional[str] = None


class Image(BaseModel):
    id: str
    name: str
    full_name: str
    original_tag: str
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    committed: Optional[datetime] = None

    @validator("committed")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


SPEC_VERSION = "v2-alpha"


class ImageSource(BaseModel):
    """
    ImageSource describes where Beaker can find a task's image.
    Beaker will automatically pull, or download, this image immediately before running the task.

    .. attention::
        One of either 'beaker' or 'docker' must be set, but not both.
    """

    beaker: Optional[str] = None
    """
    The full name or ID of a Beaker image.
    """

    docker: Optional[str] = None
    """
    The tag of a Docker image hosted on the Docker Hub or a private registry.

    .. note::
        If the tag is from a private registry, the cluster on which the task will run must
        be pre-configured to enable access.
    """

    @root_validator(pre=True)
    def _check_exactly_one_field_set(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if (values.get("beaker") is None) == (values.get("docker") is None):
            raise ValueError(
                "Exactly one of 'beaker' or 'docker' must be specified for image source"
            )
        return values


class EnvVar(BaseModel):
    """
    An EnvVar defines an environment variable within a task's container.

    .. tip::
        If neither 'source' nor 'secret' are set, the value of the environment variable
        with default to "".
    """

    name: str
    """
    Name of the environment variable following Unix rules.
    Environment variable names are case sensitive and must be unique.
    """

    value: Optional[str] = None
    """
    Literal value which can include spaces and special characters.
    """

    secret: Optional[str] = None
    """
    Source the enviroment variable from a secret in the experiment's workspace.
    """


class DataSource(BaseModel):
    """
    .. attention::
        Exactly one source field must be set.
    """

    beaker: Optional[str] = None
    """
    The full name or ID of a Beaker dataset.

    .. tip::
        Beaker datasets provide the best download performance and are preferred for
        frequently used datasets.
    """

    host_path: Optional[str] = None
    """
    Path to a file or directory on the host.

    The executing host must be configured to allow access to this path or one of its parent directories.
    Currently the following host paths are allowed on every on-premise machine managed
    by the Beaker team:

    - ``/net`` for access to NFS.
    - ``/raid`` for access to RAID.
    - ``/var/beaker/share`` as a shared local scratch space.
    """

    result: Optional[str] = None
    """
    Name of a previous task whose result will be mounted.

    .. important::
        A result source implies a dependency, meaning this task will not run until its parent
        completes successfully.
    """

    url: Optional[str] = None
    """
    URL is a web location from which to download data.
    Beaker currently supports S3 (``s3://``), GCS (``gs://``), and HTTP(S) (``https://``) URLs.
    """

    secret: Optional[str] = None
    """
    Name of a secret within the experiment's workspace which will be mounted as a plain-text file.
    """

    @root_validator(pre=True)
    def _check_exactly_one_field_set(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        print(values)
        if len([v for v in values.values() if v is not None]) != 1:
            raise ValueError("Exactly one data source field must be set.")
        return values


class DataMount(BaseModel):
    """
    Describes how to mount a dataset into a task. All datasets are mounted read-only.
    """

    source: DataSource
    """
    Location from which Beaker will download the dataset.
    """

    mount_path: str
    """
    The mount path is where Beaker will place the dataset within the task container.
    Mount paths must be absolute and may not overlap with other mounts.

    .. error::
        Because some environments use case-insensitive file systems, mount paths
        differing only in capitalization are disallowed.
    """

    sub_path: Optional[str] = None
    """
    Sub-path to a file or directory within the mounted dataset.
    Sub-paths may be used to mount only a portion of a dataset; files outside of the
    mounted path are not downloaded.

    For example, given a dataset containing a file ``/path/to/file.csv``,
    setting the sub-path to ``path/to`` will result in the task seeing ``{mount_path}/file.csv``.
    """


class ResultSpec(BaseModel):
    """
    Describes how to capture a task's results.

    Results are captured as datasets from the given location. Beaker monitors this location for
    changes and periodically uploads files as they change in near-real-time.
    """

    path: str
    """
    Directory to which the task will write output files.
    """


class TaskResources(BaseModel):
    """
    TaskResources describe minimum external hardware requirements which must be available for a
    task to run. Generally, only a GPU request is necessary.
    """

    cpu_count: Optional[float] = None
    """
    Minimum number of logical CPU cores. It may be fractional.

    Examples: ``4``, ``0.5``.

    .. tip::
        Since CPU is only limited during periods of contention, it's generally not necessary
        to specify this field.
    """

    gpu_count: Optional[int] = None
    """
    Minimum number of GPUs. It must be non-negative.
    """

    memory: Optional[str] = None
    """
    Minimum available system memory as a number with unit suffix.

    Examples: ``2.5GiB``, ``1024m``.
    """

    shared_memory: Optional[str] = None
    """
    Size of ``/dev/shm`` as a number with unit suffix. Defaults to ``5GiB``.

    Examples: ``2.5GiB``, ``1024m``.
    """


class TaskContext(BaseModel):
    """
    Describes an execution environment, or how a task should be run.

    .. important::
        Because contexts depend on external configuration, a given context may be invalid or unavailable
        if a task is re-run at a future date.
    """

    cluster: str
    """
    The full name or ID of a Beaker cluster on which the task should run.
    """

    priority: Optional[str] = None
    """
    Set priority to change the urgency with which a task will run.

    Values may be 'low', 'normal', or 'high'.
    Tasks with higher priority are placed ahead of tasks with lower priority in the queue.

    Priority may also be elevated to 'urgent' through UI.
    """

    @validator("priority")
    def _validate_priority(cls, v: str) -> str:
        if v not in {"low", "normal", "high"}:
            raise ValueError(
                "Invalided 'priority'. Value must be one of 'low', 'normal', or 'high'."
            )
        return v


class TaskSpec(BaseModel):
    """
    Tasks are Beaker's fundamental unit of work.

    A Beaker experiment may contain multiple tasks.
    A task may also depend on the results of another task in its experiment,
    creating an execution graph.
    """

    name: str
    """
    Name is used for display and to refer to the task throughout the spec.
    It must be unique among all tasks within its experiment.
    """

    image: ImageSource
    """
    A base image to run, usually built with Docker.
    """

    result: ResultSpec
    """
    Where the task will place output files.
    """

    context: TaskContext
    """
    Context describes how and where this task should run.
    """

    command: Optional[List[str]] = None
    """
    Command is the full shell command to run as a list of separate arguments.

    If omitted, the image's default command is used, for example Docker's ``ENTRYPOINT`` directive.
    If set, default commands such as Docker's ``ENTRYPOINT`` and ``CMD`` directives are ignored.

    Example: ``["python", "-u", "main.py"]``
    """

    arguments: Optional[List[str]] = None
    """
    Arguments are appended to the command and replace default arguments such as Docker's ``CMD`` directive.

    If ``command`` is omitted, arguments are appended to the default command, Docker's ``ENTRYPOINT`` directive.

    Example: If ``command`` is ``["python", "-u", "main.py"]``, specifying arguments
    ``["--quiet", "some-arg"]`` will run the command ``python -u main.py --quiet some-arg``.
    """

    env_vars: Optional[List[EnvVar]] = None
    """
    List of environment variables passed to the container.
    """

    datasets: Optional[List[DataMount]] = None
    """
    External data sources mounted into the task as files.
    """

    resources: Optional[TaskResources] = None
    """
    External hardware requirements, such as memory or GPU devices.
    """


class ExperimentSpec(BaseModel):
    """
    An experiment is the main unit of execution in Beaker.
    """

    tasks: List[TaskSpec]
    """
    Specifications for each process to run.
    """

    version: str = SPEC_VERSION
    """
    Must be 'v2-alpha' for now.
    """

    description: Optional[str] = None
    """
    Long-form explanation for an experiment.
    """

    @validator("version")
    def _validate_version(cls, v: str) -> str:
        if v != SPEC_VERSION:
            raise ValueError(f"Only version '{SPEC_VERSION}' is currently supported")
        return v
