from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from ..aliases import PathOrStr
from ..exceptions import *
from ..util import parse_duration
from .base import BaseModel, StrEnum, field_validator, model_validator

__all__ = [
    "ImageSource",
    "EnvVar",
    "DataSource",
    "DataMount",
    "ResultSpec",
    "TaskResources",
    "Priority",
    "TaskContext",
    "TaskSpec",
    "SpecVersion",
    "RetrySpec",
    "ExperimentSpec",
    "Constraints",
]


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


class EnvVar(BaseModel, frozen=False):
    """
    An :class:`EnvVar` defines an environment variable within a task's container.

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

    weka: Optional[str] = None
    """
    The name of a weka bucket.
    """

    result: Optional[str] = None
    """
    Name of a previous task whose result will be mounted.

    .. important::
        A result source implies a dependency, meaning this task will not run until its parent
        completes successfully.
    """

    secret: Optional[str] = None
    """
    Name of a secret within the experiment's workspace which will be mounted as a plain-text file.
    """

    @model_validator(mode="before")
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
        weka: Optional[str] = None,
        result: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> "DataMount":
        """
        A convenience method for quickly creating a new :class:`DataMount`.

        :param mount_path: The :data:`mount_path`.
        :param sub_path: The :data:`sub_path`.
        :param beaker: The :data:`beaker <DataSource.beaker>` argument to :class:`DataSource`.
        :param host_path: The :data:`host_path <DataSource.host_path>` argument to :class:`DataSource`.
        :param weka: The :data:`weka <DataSource.weka>` argument to :class:`DataSource`.
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
                weka=weka,
                result=result,
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


class Priority(StrEnum):
    """
    Defines the urgency with which a task will run.
    """

    immediate = "immediate"
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

    cluster: Optional[str] = None
    """
    The full name or ID of a Beaker cluster on which the task should run.

    .. attention::
        This field is deprecated. See :data:`TaskSpec.constraints` instead.
    """

    priority: Optional[Priority] = None
    """
    Set priority to change the urgency with which a task will run.
    Tasks with higher priority are placed ahead of tasks with lower priority in the queue.
    """

    preemptible: Optional[bool] = None
    """
    Whether or not a job is marked as preemptible.
    """

    @field_validator("priority")
    def _validate_priority(cls, v: str) -> str:
        if v is not None and v not in set(Priority):
            raise ValueError(
                f"Invalided 'priority'. Value must be one of {[p.value for p in Priority]} (got '{v}')."
            )
        return v


class Constraints(BaseModel, frozen=False, extra="allow"):
    """
    Constraints are specified via the :data:`~TaskSpec.constraints` field in :class:`TaskSpec`.

    This type also allows other fields that are not listed here.
    """

    cluster: Optional[List[str]] = None
    """
    A list of cluster names or IDs on which the task is allowed to be executed.
    You are allowed to omit this field for tasks that have preemptible priority,
    in which case the task will run on any cluster where you have permissions.
    """

    hostname: Optional[List[str]] = None
    """
    Hostname constraints.
    """

    def __setitem__(self, key: str, val: List[Any]) -> None:
        setattr(self, key, val)


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

    constraints: Optional[Constraints] = None
    """
    Each task can have many constraints. And each constraint can have many values.
    Constraints are rules that change where a task is executed,
    by influencing the scheduler's placement of the workload.

    .. important::
        Because constraints depend on external configuration, a given constraints may be invalid or unavailable
        if a task is re-run at a future date.
    """

    name: Optional[str] = None
    """
    Name is used for display and to refer to the task throughout the spec.
    It must be unique among all tasks within its experiment.
    """

    command: Optional[List[Union[str, int, float]]] = None
    """
    Command is the full shell command to run as a sequence of separate arguments.

    If omitted, the image's default command is used, for example Docker's ``ENTRYPOINT`` directive.
    If set, default commands such as Docker's ``ENTRYPOINT`` and ``CMD`` directives are ignored.

    Example: ``["python", "-u", "main.py"]``
    """

    arguments: Optional[List[Union[str, int, float]]] = None
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

    host_networking: bool = False
    """
    Enables the task to use the host's network.
    """

    replicas: Optional[int] = None
    """
    The number of replica tasks to create based on this template.
    """

    leader_selection: bool = False
    """
    Enables leader selection for the replicas and passes the leader's hostname to the replicas.
    """

    propagate_failure: Optional[bool] = None
    """
    Determines if whole experiment should fail if this task failures.
    """

    propagate_preemption: Optional[bool] = None
    """
    Determines if all tasks should be preempted if this one task is.
    """

    synchronized_start_timeout: Optional[int] = None
    """
    If set, jobs in the replicated task will wait to start, up to the specified timeout, 
    until all other jobs are also ready. If the timeout is reached, the job will be canceled.
    Represented using nanoseconds, must be greater than zero and less than or equal to 48 hours.
    """

    timeout: Optional[int] = None
    """
    Timeout for jobs in the task.
    """

    @field_validator("synchronized_start_timeout", "timeout", mode="before")
    @classmethod
    def ensure_nanoseconds(cls, value: Any) -> int:
        if isinstance(value, str):
            return parse_duration(value)
        else:
            return value

    @classmethod
    def new(
        cls,
        name: str,
        cluster: Optional[Union[str, List[str]]] = None,
        beaker_image: Optional[str] = None,
        docker_image: Optional[str] = None,
        result_path: str = "/unused",
        priority: Optional[Union[str, Priority]] = None,
        preemptible: Optional[bool] = None,
        **kwargs,
    ) -> "TaskSpec":
        """
        A convenience method for quickly creating a new :class:`TaskSpec`.

        :param name: The :data:`name` of the task.
        :param cluster: The cluster or clusters where the experiment can run.

            .. tip::
                Omitting the cluster will allow your experiment to run on *any* on-premise
                cluster, but you can only do this with preemptible jobs.

        :param beaker_image: The :data:`beaker <ImageSource.beaker>` image name in the
            :data:`image` source.

            .. important::
                Mutually exclusive with ``docker_image``.

        :param docker_image: The :data:`docker <ImageSource.docker>` image name in the
            :data:`image` source.

            .. important::
                Mutually exclusive with ``beaker_image``.

        :param priority: The :data:`priority <TaskContext.priority>` of the :data:`context`.
        :param preemptible: If the task should be preemptible.
        :param kwargs: Additional kwargs are passed as-is to :class:`TaskSpec`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     cluster="ai2/cpu-cluster",
        ...     docker_image="hello-world",
        ... )
        """
        constraints = kwargs.pop("constraints", None)
        if constraints is not None and not isinstance(constraints, Constraints):
            constraints = Constraints(**constraints)

        if cluster is not None:
            if constraints is not None and constraints.cluster:
                raise ValueError("'cluster' can only be specified one way")
            if isinstance(cluster, list):
                if constraints is not None:
                    constraints.cluster = cluster
                else:
                    constraints = Constraints(cluster=cluster)
            elif isinstance(cluster, str):
                if constraints is not None:
                    constraints.cluster = [cluster]
                else:
                    constraints = Constraints(cluster=[cluster])

        return TaskSpec(
            name=name,
            image=ImageSource(beaker=beaker_image, docker=docker_image),
            result=ResultSpec(path=result_path),
            context=TaskContext(
                priority=None if priority is None else Priority(priority), preemptible=preemptible
            ),
            constraints=constraints,
            **kwargs,
        )

    def with_image(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`image`.

        :param kwargs: Key-word arguments that are passed directly to :class:`ImageSource`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_image(beaker="hello-world")
        >>> assert task_spec.image.beaker == "hello-world"
        """
        return self.model_copy(deep=True, update={"image": ImageSource(**kwargs)})

    def with_result(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`result`.

        :param kwargs: Key-word arguments that are passed directly to :class:`ResultSpec`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_result(path="/output")
        >>> assert task_spec.result.path == "/output"
        """
        return self.model_copy(deep=True, update={"result": ResultSpec(**kwargs)})

    def with_context(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`context`.

        :param kwargs: Key-word arguments that are passed directly to :class:`TaskContext`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_context(cluster="ai2/general-cirrascale")
        >>> assert task_spec.context.cluster == "ai2/general-cirrascale"
        """
        return self.model_copy(deep=True, update={"context": TaskContext(**kwargs)})

    def with_name(self, name: str) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`name`.

        :param name: The new name.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_name("Hi there!")
        >>> assert task_spec.name == "Hi there!"
        """
        return self.model_copy(deep=True, update={"name": name})

    def with_command(self, command: List[str]) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`command`.

        :param command: The new command.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_command(["echo"])
        >>> assert task_spec.command == ["echo"]
        """
        return self.model_copy(deep=True, update={"command": command})

    def with_arguments(self, arguments: List[str]) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`arguments`.

        :param arguments: The new arguments.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_arguments(["Hello", "World!"])
        >>> assert task_spec.arguments == ["Hello", "World!"]
        """
        return self.model_copy(deep=True, update={"arguments": arguments})

    def with_resources(self, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`resources`.

        :param kwargs: Key-word arguments are passed directly to :class:`TaskResources`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_resources(gpu_count=2)
        >>> assert task_spec.resources.gpu_count == 2
        """
        return self.model_copy(deep=True, update={"resources": TaskResources(**kwargs)})

    def with_dataset(self, mount_path: str, **kwargs) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with an additional input :data:`dataset <datasets>`.

        :param mount_path: The :data:`mount_path <DataMount>` of the :class:`DataMount`.
        :param kwargs: Additional kwargs are passed as-is to :meth:`DataMount.new()`.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_dataset("/data/foo", beaker="foo")
        >>> assert task_spec.datasets
        """
        return self.model_copy(
            deep=True,
            update={
                "datasets": [d.model_copy(deep=True) for d in self.datasets or []]
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
        ...     docker_image="hello-world",
        ...     env_vars=[EnvVar(name="bar", value="secret!")],
        ... ).with_env_var("baz", value="top, top secret")
        >>> assert len(task_spec.env_vars) == 2
        """
        return self.model_copy(
            deep=True,
            update={
                "env_vars": [d.model_copy(deep=True) for d in self.env_vars or []]
                + [EnvVar(name=name, value=value, secret=secret)]
            },
        )

    def with_constraint(self, **kwargs: List[str]) -> "TaskSpec":
        """
        Return a new :class:`TaskSpec` with the given :data:`constraints`.

        :param kwargs: Constraint name, constraint values.

        :examples:

        >>> task_spec = TaskSpec.new(
        ...     "hello-world",
        ...     docker_image="hello-world",
        ... ).with_constraint(cluster=['ai2/cpu-cluster'])
        >>> assert task_spec.constraints['cluster'] == ['ai2/cpu-cluster']
        """
        constraints = (
            Constraints(**kwargs)
            if self.constraints is None
            else self.constraints.model_copy(deep=True, update=kwargs)
        )
        return self.model_copy(
            deep=True,
            update={
                "constraints": constraints,
            },
        )


class SpecVersion(StrEnum):
    v2 = "v2"
    v2_alpha = "v2-alpha"


class RetrySpec(BaseModel, frozen=False):
    """
    Defines the retry behavior of an experiment.
    """

    allowed_task_retries: Optional[int] = None
    """
    A positive integer specifying the maximum number of task retries allowed for the experiment,
    with a max limit of 10.
    """


class ExperimentSpec(BaseModel, frozen=False):
    """
    Experiments are the main unit of execution in Beaker.

    An :class:`ExperimentSpec` defines an :class:`~beaker.data_model.experiment.Experiment`.

    :examples:

    >>> spec = ExperimentSpec(
    ...     budget="ai2/allennlp",
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

    budget: str
    """
    The name of the budget account for your team.
    See https://beaker-docs.apps.allenai.org/concept/budgets.html for more details.
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

    retry: Optional[RetrySpec] = None
    """
    Defines the retry behavior of an experiment.
    """

    @field_validator("tasks")
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

    @classmethod
    def new(
        cls,
        budget: str,
        task_name: str = "main",
        description: Optional[str] = None,
        cluster: Optional[Union[str, List[str]]] = None,
        beaker_image: Optional[str] = None,
        docker_image: Optional[str] = None,
        result_path: str = "/unused",
        priority: Optional[Union[str, Priority]] = None,
        **kwargs,
    ) -> "ExperimentSpec":
        """
        A convenience method for creating a new :class:`ExperimentSpec` with a single task.

        :param task_name: The name of the task.
        :param description: A description of the experiment.
        :param cluster: The cluster or clusters where the experiment can run.

            .. tip::
                Omitting the cluster will allow your experiment to run on *any* on-premise
                cluster, but you can only do this with preemptible jobs.

        :param beaker_image: The :data:`beaker <ImageSource.beaker>` image name in the
            :data:`image` source.
        :param docker_image: The :data:`docker <ImageSource.docker>` image name in the
            :data:`image` source.

            .. important::
                Mutually exclusive with ``beaker_image``.

        :param priority: The :data:`priority <TaskContext.priority>` of the :data:`context`.
        :param kwargs: Additional kwargs are passed as-is to :class:`TaskSpec`.

        :examples:

        Create a preemptible experiment that can run an any on-premise cluster:

        >>> spec = ExperimentSpec.new(
        ...     "ai2/allennlp",
        ...     docker_image="hello-world",
        ...     priority=Priority.preemptible,
        ... )
        """
        return cls(
            budget=budget,
            description=description,
            tasks=[
                TaskSpec.new(
                    task_name,
                    cluster=cluster,
                    beaker_image=beaker_image,
                    docker_image=docker_image,
                    result_path=result_path,
                    priority=priority,
                    **kwargs,
                )
            ],
        )

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

        >>> spec = ExperimentSpec(budget="ai2/allennlp").with_task(
        ...     TaskSpec.new(
        ...         "hello-world",
        ...         docker_image="hello-world",
        ...     )
        ... )
        """
        if task.name is not None:
            for other_task in self.tasks:
                if task.name == other_task.name:
                    raise ValueError(f"A task with the name '{task.name}' already exists")
        return self.model_copy(
            deep=True,
            update={"tasks": [d.model_copy(deep=True) for d in self.tasks or []] + [task]},
        )

    def with_description(self, description: str) -> "ExperimentSpec":
        """
        Return a new :class:`ExperimentSpec` with a different description.

        :param description: The new description.

        :examples:

        >>> ExperimentSpec(budget="ai2/allennlp", description="Hello, World!").with_description(
        ...     "Hello, Mars!"
        ... ).description
        'Hello, Mars!'
        """
        return self.model_copy(deep=True, update={"description": description})

    def with_retries(self, allowed_task_retries: int) -> "ExperimentSpec":
        """
        Return a new :class:`ExperimentSpec` with the given number of retries.
        """
        return self.model_copy(
            deep=True, update={"retry": RetrySpec(allowed_task_retries=allowed_task_retries)}
        )

    def validate(self):
        for task in self.tasks:
            if (task.image.beaker is None) == (task.image.docker is None):
                raise ExperimentSpecError(
                    "Exactly one of 'beaker' or 'docker' must be specified for image source"
                )
