from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, root_validator, validator

from ..aliases import PathOrStr
from .base import BaseModel


class ImageSource(BaseModel, frozen=False):
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


class EnvVar(BaseModel, frozen=False):
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


class DataSource(BaseModel, frozen=False):
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
        if len([v for v in values.values() if v is not None]) != 1:
            raise ValueError("Exactly one data source field must be set.")
        return values


class DataMount(BaseModel, frozen=False):
    """
    Describes how to mount a dataset into a task. All datasets are mounted read-only.

    .. seealso::
        This is used in the :data:`TaskSpec.datasets` property in :class:`TaskSpec`.
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

    @classmethod
    def new(
        cls,
        mount_path: str,
        sub_path: Optional[str] = None,
        beaker: Optional[str] = None,
        host_path: Optional[str] = None,
        result: Optional[str] = None,
        url: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> "DataMount":
        """
        A convenience method for quickly creating a new :class:`DataMount`.

        :param mount_path: The :data:`mount_path`.
        :param sub_path: The :data:`sub_path`.
        :param beaker: The :data:`beaker <DataSource.beaker>` argument to :class:`DataSource`.
        :param host_path: The :data:`host_path <DataSource.host_path>` argument to :class:`DataSource`.
        :param result: The :data:`result <DataSource.result>` argument to :class:`DataSource`.
        :param url: The :data:`url <DataSource.url>` argument to :class:`DataSource`.
        :param secret: The :data:`secret <DataSource.secret>` argument to :class:`DataSource`.
        """
        return cls(
            mount_path=mount_path,
            sub_path=sub_path,
            source=DataSource(
                beaker=beaker,
                host_path=host_path,
                result=result,
                url=url,
                secret=secret,
            ),
        )


class ResultSpec(BaseModel, frozen=False):
    """
    Describes how to capture a task's results.

    Results are captured as datasets from the given location. Beaker monitors this location for
    changes and periodically uploads files as they change in near-real-time.
    """

    path: str
    """
    Directory to which the task will write output files.
    """


class TaskResources(BaseModel, frozen=False):
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


class Priority(str, Enum):
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"
    preemptible = "preemptible"


class TaskContext(BaseModel, frozen=False):
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

    priority: Optional[Priority] = None
    """
    Set priority to change the urgency with which a task will run.

    Values may be 'low', 'normal', or 'high'.
    Tasks with higher priority are placed ahead of tasks with lower priority in the queue.

    Priority may also be elevated to 'urgent' through UI.
    """

    @validator("priority")
    def _validate_priority(cls, v: str) -> str:
        if v is not None and v not in {"preemptible", "low", "normal", "high"}:
            raise ValueError(
                "Invalided 'priority'. Value must be one of 'preemptible', 'low', 'normal', or 'high'."
            )
        return v


class TaskSpec(BaseModel, frozen=False):
    """
    A :class:`TaskSpec` defines a :class:`~beaker.data_model.experiment.Task` within an :class:`ExperimentSpec`.

    Tasks are Beaker's fundamental unit of work.

    A Beaker experiment may contain multiple tasks.
    A task may also depend on the results of another task in its experiment,
    creating an execution graph.
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

    name: Optional[str] = None
    """
    Name is used for display and to refer to the task throughout the spec.
    It must be unique among all tasks within its experiment.
    """

    command: Optional[List[str]] = None
    """
    Command is the full shell command to run as a sequence of separate arguments.

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
    Sequence of environment variables passed to the container.
    """

    datasets: Optional[List[DataMount]] = None
    """
    External data sources mounted into the task as files.
    """

    resources: Optional[TaskResources] = None
    """
    External hardware requirements, such as memory or GPU devices.
    """

    @classmethod
    def new(
        cls,
        name: str,
        cluster: str,
        beaker_image: Optional[str] = None,
        docker_image: Optional[str] = None,
        result_path: str = "/unused",
        priority: Optional[str] = None,
        **kwargs,
    ) -> "TaskSpec":
        """
        A convenience method for quickly creating a new :class:`TaskSpec`.

        :param name: The :data:`name` of the task.
        :param cluster: The :data:`cluster <TaskContext.cluster>` name in the :data:`context`.
        :param beaker_image: The :data:`beaker <ImageSource.beaker>` image name in the
            :data:`image` source.

            .. important::
                Mutually exclusive with ``docker_image``.

        :param docker_image: The :data:`docker <ImageSource.docker>` image name in the
            :data:`image` source.

            .. important::
                Mutually exclusive with ``beaker_image``.

        :param priority: The :data:`priority <TaskContext.priority>` of the :data:`context`.
        :param kwargs: Additional kwargs are passed as-is to :class:`TaskSpec`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/cpu-cluster",
        ...     docker_image="hello-world",
        ... )
        """
        return TaskSpec(
            name=name,
            image=ImageSource(beaker=beaker_image, docker=docker_image),
            result=ResultSpec(path=result_path),
            context=TaskContext(cluster=cluster, priority=priority),
            **kwargs,
        )

    def with_image(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`image`.

        :param kwargs: Key-word arguments that are passed directly to :class:`ImageSource`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_image(beaker="hello-world")
        >>> assert task_spec.image.beaker == "hello-world"
        """
        return self.copy(deep=True, update={"image": ImageSource(**kwargs)})

    def with_result(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`result`.

        :param kwargs: Key-word arguments that are passed directly to :class:`ResultSpec`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_result(path="/output")
        >>> assert task_spec.result.path == "/output"
        """
        return self.copy(deep=True, update={"result": ResultSpec(**kwargs)})

    def with_context(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`context`.

        :param kwargs: Key-word arguments that are passed directly to :class:`TaskContext`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_context(cluster="ai2/general-cirrascale")
        >>> assert task_spec.context.cluster == "ai2/general-cirrascale"
        """
        return self.copy(deep=True, update={"context": TaskContext(**kwargs)})

    def with_name(self, name: str) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`name`.

        :param name: The new name.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_name("Hi there!")
        >>> assert task_spec.name == "Hi there!"
        """
        return self.copy(deep=True, update={"name": name})

    def with_command(self, command: List[str]) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`command`.

        :param command: The new command.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_command(["echo"])
        >>> assert task_spec.command == ["echo"]
        """
        return self.copy(deep=True, update={"command": command})

    def with_arguments(self, arguments: List[str]) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`arguments`.

        :param arguments: The new arguments.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_arguments(["Hello", "World!"])
        >>> assert task_spec.arguments == ["Hello", "World!"]
        """
        return self.copy(deep=True, update={"arguments": arguments})

    def with_resources(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`resources`.

        :param kwargs: Key-word arguments are passed directly to :class:`TaskResources`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/gpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_resources(gpu_count=2)
        >>> assert task_spec.resources.gpu_count == 2
        """
        return self.copy(deep=True, update={"resources": TaskResources(**kwargs)})

    def with_dataset(self, mount_path: str, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with an additional input :data:`dataset <datasets>`.

        :param mount_path: The :data:`mount_path <DataMount>` of the :class:`DataMount`.
        :param kwargs: Additional kwargs are passed as-is to :meth:`DataMount.new()`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/cpu-cluster",
        ...     docker_image="hello-world",
        ... ).with_dataset("/data/foo", beaker="foo")
        >>> assert task_spec.datasets
        """
        return self.copy(
            deep=True,
            update={
                "datasets": [d.copy(deep=True) for d in self.datasets or []]
                + [DataMount.new(mount_path, **kwargs)]
            },
        )

    def with_env_var(
        self, name: str, value: Optional[str] = None, secret: Optional[str] = None
    ) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with an additional input :data:`env_var <env_vars>`.

        :param name: The :data:`name <EnvVar.name>` of the :class:`EnvVar`.
        :param value: The :data:`value <EnvVar.value>` of the :class:`EnvVar`.
        :param secret: The :data:`secret <EnvVar.secret>` of the :class:`EnvVar`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     "ai2/cpu-cluster",
        ...     docker_image="hello-world",
        ...     env_vars=[EnvVar(name="bar", value="secret!")],
        ... ).with_env_var("baz", value="top, top secret")
        >>> assert len(task_spec.env_vars) == 2
        """
        return self.copy(
            deep=True,
            update={
                "env_vars": [d.copy(deep=True) for d in self.env_vars or []]
                + [EnvVar(name=name, value=value, secret=secret)]
            },
        )


class SpecVersion(str, Enum):
    v2 = "v2"
    v2_alpha = "v2-alpha"


class ExperimentSpec(BaseModel, frozen=False):
    """
    Experiments are the main unit of execution in Beaker.

    An :class:`ExperimentSpec` defines an :class:`~beaker.data_model.experiment.Experiment`.

    :examples:

    >>> spec = ExperimentSpec(
    ...     tasks=[
    ...         TaskSpec(
    ...             name="hello",
    ...             image=ImageSource(docker="hello-world"),
    ...             context=TaskContext(cluster="ai2/cpu-only"),
    ...             result=ResultSpec(
    ...                 path="/unused"  # required even if the task produces no output.
    ...             ),
    ...         ),
    ...     ],
    ... )
    """

    tasks: List[TaskSpec] = Field(default_factory=tuple)
    """
    Specifications for each process to run.
    """

    version: SpecVersion = SpecVersion.v2
    """
    Must be 'v2' for now.
    """

    description: Optional[str] = None
    """
    Long-form explanation for an experiment.
    """

    @validator("tasks")
    def _validate_tasks(cls, v: List[TaskSpec]) -> List[TaskSpec]:
        task_names = set()
        for task in v:
            if task.name is None:
                continue
            if task.name in task_names:
                raise ValueError(f"Duplicate task name '{task.name}'")
            else:
                task_names.add(task.name)
        return v

    @classmethod
    def from_file(cls, path: PathOrStr) -> "ExperimentSpec":
        """
        Load an :class:`ExperimentSpec` from a YAML file.
        """
        import yaml

        with open(path) as spec_file:
            raw_spec = yaml.load(spec_file, Loader=yaml.SafeLoader)
            return cls.from_json(raw_spec)

    def to_file(self, path: PathOrStr) -> None:
        """
        Write the experiment spec to a YAML file.
        """
        import yaml

        raw_spec = self.to_json()
        with open(path, "wt") as spec_file:
            yaml.dump(raw_spec, spec_file, Dumper=yaml.SafeDumper)

    def with_task(self, task: TaskSpec) -> "ExperimentSpec":
        """
        Return a new :class:`ExperimentSpec` with an additional task.

        :param task: The task to add.

        :examples:

        >>> spec = ExperimentSpec().with_task(
        ...     TaskSpec.new(
        ...         "hello-world",
        ...         "ai2/cpu-cluster",
        ...         docker_image="hello-world",
        ...     )
        ... )
        """
        if task.name is not None:
            for other_task in self.tasks:
                if task.name == other_task.name:
                    raise ValueError(f"A task with the name '{task.name}' already exists")
        return self.copy(
            deep=True, update={"tasks": [d.copy(deep=True) for d in self.tasks or []] + [task]}
        )

    def with_description(self, description: str) -> "ExperimentSpec":
        """
        Return a new :class:`ExperimentSpec` with a different description.

        :param description: The new description.

        :examples:

        >>> ExperimentSpec(description="Hello, World!").with_description(
        ...     "Hello, Mars!"
        ... ).description
        'Hello, Mars!'
        """
        return self.copy(deep=True, update={"description": description})
