import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from ..progress import get_exps_and_jobs_progress
from .service_client import ServiceClient

if TYPE_CHECKING:
    from rich.progress import TaskID


class ExperimentClient(ServiceClient):
    """
    Accessed via :data:`Beaker.experiment <beaker.Beaker.experiment>`.
    """

    def get(self, experiment: str) -> Experiment:
        """
        Get info about an experiment.

        :param experiment: The experiment ID or name.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """

        def _get(id: str) -> Experiment:
            return Experiment.from_json(
                self.request(
                    f"experiments/{self.url_quote(id)}",
                    exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be an ID or full name, so we try that first.
            return _get(experiment)
        except ExperimentNotFound:
            if "/" not in experiment:
                # Try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{experiment}")
                except ExperimentNotFound:
                    pass

                # Try searching the default workspace.
                if self.config.default_workspace is not None:
                    matches = self.beaker.workspace.experiments(match=experiment, limit=1)
                    if matches:
                        return matches[0]
            raise

    def _parse_create_args(
        self, *args, **kwargs
    ) -> Tuple[Union[ExperimentSpec, PathOrStr], Optional[str], Optional[Union[Workspace, str]]]:
        spec: Optional[Union[ExperimentSpec, PathOrStr]] = kwargs.pop("spec", None)
        name: Optional[str] = kwargs.pop("name", None)
        workspace: Optional[Union[Workspace, str]] = kwargs.pop("workspace", None)
        if len(args) == 3:
            if name is not None or spec is not None or workspace is not None:
                raise TypeError(
                    "ExperimentClient.create() got an unexpected number of positional arguments"
                )
            if (
                isinstance(args[0], str)
                and isinstance(args[1], (ExperimentSpec, Path, str))
                and isinstance(
                    args[2],
                    (
                        str,
                        Workspace,
                    ),
                )
            ):
                name, spec, workspace = args
            elif (
                isinstance(args[0], (ExperimentSpec, Path, str))
                and isinstance(args[1], str)
                and isinstance(
                    args[2],
                    (
                        str,
                        Workspace,
                    ),
                )
            ):
                spec, name, workspace = args
            else:
                raise TypeError("ExperimentClient.create() got an unexpected positional argument")
        elif len(args) == 2:
            if name is not None or spec is not None:
                raise TypeError(
                    "ExperimentClient.create() got an unexpected number of positional arguments"
                )
            if isinstance(args[0], str) and isinstance(args[1], (ExperimentSpec, Path, str)):
                name, spec = args
            elif isinstance(args[0], (ExperimentSpec, Path, str)) and isinstance(args[1], str):
                spec, name = args
            else:
                raise TypeError("ExperimentClient.create() got an unexpected positional argument")
        elif len(args) == 1:
            if spec is None:
                spec = args[0]
            elif name is None:
                name = args[0]
            else:
                raise TypeError("ExperimentClient.create() got an unexpected positional argument")
        elif len(args) != 0:
            raise TypeError(
                "ExperimentClient.create() got an unexpected number of positional arguments"
            )
        elif spec is None:
            raise TypeError("ExperimentClient.create() is missing 1 required argument: 'spec'")

        if kwargs:
            raise TypeError(
                f"ExperimentClient.create() got unexpected keyword arguments {tuple(kwargs.keys())}"
            )

        assert spec is not None
        return spec, name, workspace

    def list(
        self,
        *,
        author: Optional[Union[str, Account]] = None,
        cluster: Optional[Union[str, Cluster]] = None,
        finalized: bool = False,
        node: Optional[Union[str, Node]] = None,
    ) -> List[Experiment]:
        """
        List experiments.

        :param author: List only experiments by particular author.
        :param cluster: List experiments on a particular cluster.
        :param finalized: List only finalized or non-finalized experiments.
        :param node: List experiments on a particular node.

        .. important::
            Either ``cluster``, ``author``, ``experiment``, or ``node`` must be specified.
            If ``node`` is specified, neither ``cluster`` nor ``experiment`` can be
            specified.

        :raises ValueError: If the arguments are invalid, e.g. both ``node`` and
            ``cluster`` are specified.
        :raises AccountNotFound: If the specified author doesn't exist.
        :raises ClusterNotFound: If the specified cluster doesn't exist.
        :raises NodeNotFound: If the specified node doesn't exist.
        """
        jobs = self.beaker.job.list(
            author=author, cluster=cluster, finalized=finalized, kind=JobKind.execution, node=node
        )
        experiments: List[Experiment] = []
        exp_ids: Set[str] = set()
        for job in jobs:
            assert job.execution is not None
            if (exp_id := job.execution.experiment) not in exp_ids:
                exp_ids.add(exp_id)
                experiments.append(self.get(exp_id))
        return experiments

    def create(
        self,
        *args,
        **kwargs,
    ) -> Experiment:
        """
        Create a new Beaker experiment with the given ``spec``.

        :param spec: The spec for the Beaker experiment. This can either be an
            :class:`~beaker.data_model.experiment_spec.ExperimentSpec` instance or the path to a YAML spec file.
        :type spec: :class:`~beaker.data_model.experiment_spec.ExperimentSpec` | :class:`~pathlib.Path` | :class:`str`
        :param name: An optional name to assign the experiment. Must be unique.
        :type name: :class:`str`, optional
        :param workspace: An optional workspace to create the experiment under. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :type workspace: :class:`~beaker.data_model.workspace.Workspace` | :class:`str`, optional

        :raises ValueError: If the name is invalid.
        :raises ExperimentConflict: If an experiment with the given name already exists.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

        """
        spec, name, workspace = self._parse_create_args(*args, **kwargs)
        # For backwards compatibility we parse out the arguments like this to allow for `create(name, spec)`
        # or just `create(spec)`.
        if name is not None:
            self.validate_beaker_name(name)
        if not isinstance(spec, ExperimentSpec):
            spec = ExperimentSpec.from_file(spec)
        spec.validate()
        json_spec = spec.to_json()
        workspace = self.resolve_workspace(workspace)
        self._validate_spec(spec, workspace)
        experiment_data = self.request(
            f"workspaces/{workspace.id}/experiments",
            method="POST",
            query=None if name is None else {"name": name},
            data=json_spec,
            exceptions_for_status=None if name is None else {409: ExperimentConflict(name)},
        ).json()
        return self.get(experiment_data["id"])

    def spec(self, experiment: Union[str, Experiment]) -> ExperimentSpec:
        """
        Get the :class:`spec <beaker.data_model.experiment_spec.ExperimentSpec>` of an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment_id = self.resolve_experiment(experiment).id
        spec_json = self.request(
            f"experiments/{self.url_quote(experiment_id)}/spec",
            query={"version": SpecVersion.v2.value},
            headers={"Accept": "application/json"},
        ).json()
        if "budget" not in spec_json:
            spec_json["budget"] = ""
        return ExperimentSpec.from_json(spec_json)

    def stop(self, experiment: Union[str, Experiment]):
        """
        Stop an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises ExperimentConflict: If the experiment was already stopped.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment_id = self.resolve_experiment(experiment).id
        self.request(
            f"experiments/{self.url_quote(experiment_id)}/stop",
            method="PUT",
            exceptions_for_status={
                404: ExperimentNotFound(self._not_found_err_msg(experiment)),
                409: ExperimentConflict("Experiment already stopped"),
            },
        )

    def resume(self, experiment: Union[str, Experiment]):
        """
        Resume a preempted experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment_id = self.resolve_experiment(experiment).id
        self.request(
            f"experiments/{self.url_quote(experiment_id)}/resume",
            method="POST",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment))},
        )

    def delete(self, experiment: Union[str, Experiment], delete_results_datasets: bool = True):
        """
        Delete an experiment.

        :param experiment: The experiment ID, name, or object.
        :param delete_results_datasets: Also delete the experiment's results datasets.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment = self.resolve_experiment(experiment)
        if delete_results_datasets:
            for task in self.tasks(experiment):
                for job in task.jobs:
                    try:
                        dataset = self.beaker.job.results(job)
                        if dataset is not None:
                            self.beaker.dataset.delete(dataset)
                    except DatasetNotFound:
                        pass
        self.request(
            f"experiments/{self.url_quote(experiment.id)}",
            method="DELETE",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment.id))},
        )

    def rename(self, experiment: Union[str, Experiment], name: str) -> Experiment:
        """
        Rename an experiment.

        :param experiment: The experiment ID, name, or object.
        :param name: The new name for the experiment.

        :raises ValueError: If the new name is invalid.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        self.validate_beaker_name(name)
        experiment_id = self.resolve_experiment(experiment).id
        return Experiment.from_json(
            self.request(
                f"experiments/{self.url_quote(experiment_id)}",
                method="PATCH",
                data=ExperimentPatch(name=name),
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment)),
                    409: ExperimentConflict(name),
                },
            ).json()
        )

    def set_description(self, experiment: Union[str, Experiment], description: str) -> Experiment:
        """
        Set the description of an experiment.

        :param experiment: The experiment ID, name, or object.
        :param description: The new description for the experiment.

        :raises ValueError: If the new name is invalid.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment_id = self.resolve_experiment(experiment).id
        return Experiment.from_json(
            self.request(
                f"experiments/{self.url_quote(experiment_id)}",
                method="PATCH",
                data=ExperimentPatch(description=description),
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment)),
                },
            ).json()
        )

    def tasks(self, experiment: Union[str, Experiment]) -> Tasks:
        """
        List the tasks in an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

        :examples:

        >>> task = beaker.experiment.tasks(hello_world_experiment_name)["main"]

        """
        experiment_id = self.resolve_experiment(experiment).id
        tasks = [
            Task.from_json(d)
            for d in self.request(
                f"experiments/{self.url_quote(experiment_id)}/tasks",
                method="GET",
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment))
                },
            ).json()
        ]
        return Tasks(tasks)

    def logs(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        quiet: bool = False,
        since: Optional[Union[str, "datetime", "timedelta"]] = None,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. important::
            When there are multiple jobs for the given experiment / task, the logs for the latest job
            will be returned.

        .. seealso::
            :meth:`structured_logs()`

        .. seealso::
            :meth:`Beaker.job.logs() <JobClient.logs>`

        :param experiment: The experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to fetch logs for. Required if there are multiple tasks in the experiment.
        :param quiet: If ``True``, progress won't be displayed.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC), a timestamp string in the form of RFC 3339
            (e.g. "2013-01-02T13:23:37Z"), or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).

        :raises ValueError: The experiment has no tasks or jobs, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        exp = self.resolve_experiment(experiment)
        job = self.latest_job(exp, task=task, ensure_finalized=False)
        if job is None:
            if task is None:
                raise ValueError(f"Experiment {exp.id} has no jobs")
            else:
                raise ValueError(
                    f"Experiment {exp.id} has no jobs for task "
                    f"'{task if isinstance(task, str) else task.display_name}'"
                )
        return self.beaker.job.logs(job.id, quiet=quiet, since=since)

    def structured_logs(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        quiet: bool = False,
        since: Optional[Union[datetime, timedelta]] = None,
        tail_lines: Optional[int] = None,
        follow: Optional[bool] = None,
    ) -> Generator[JobLog, None, None]:
        """
        Download/stream structured :class:`~beaker.data_model.job.JobLog` objects from an experiment.

        Returns a generator of log objects.

        .. important::
            When there are multiple jobs for the given experiment / task, the logs for the latest job
            will be returned.

        .. seealso::
            :meth:`logs()`

        .. seealso::
            :meth:`Beaker.job.structured_logs() <JobClient.logs>`

        :param experiment: The experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to fetch logs for. Required if there are multiple tasks in the experiment.
        :param quiet: If ``True``, progress won't be displayed.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC) or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).
        :param tail_lines: Start tailing with the last ``tail_lines`` lines.
        :param follow: Keep streaming as new log lines come in.

        :raises ValueError: The experiment has no tasks or jobs, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises RpcError: Any other RPC error.
        """
        exp = self.resolve_experiment(experiment)
        job = self.latest_job(exp, task=task, ensure_finalized=False)
        if job is None:
            if task is None:
                raise ValueError(f"Experiment {exp.id} has no jobs")
            else:
                raise ValueError(
                    f"Experiment {exp.id} has no jobs for task "
                    f"'{task if isinstance(task, str) else task.display_name}'"
                )
        return self.beaker.job.structured_logs(
            job.id, quiet=quiet, since=since, tail_lines=tail_lines, follow=follow
        )

    def metrics(
        self, experiment: Union[str, Experiment], task: Optional[Union[str, Task]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the metrics from a task in an experiment.

        .. important::
            When there are multiple jobs for the given experiment / task, the metrics for
            the latest finalized job will be returned.

        .. seealso::
            :meth:`Beaker.job.metrics() <JobClient.metrics>`

        :param experiment: The experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to fetch metrics for. Required if there are multiple tasks in the experiment.

        :raises ValueError: The experiment has no tasks, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        exp = self.resolve_experiment(experiment)
        job = self.latest_job(exp, task=task, ensure_finalized=True)
        return None if job is None else self.beaker.job.metrics(job.id)

    def results(
        self, experiment: Union[str, Experiment], task: Optional[Union[str, Task]] = None
    ) -> Optional[Dataset]:
        """
        Get the result dataset from a task in an experiment.

        .. important::
            When there are multiple jobs for the given experiment / task, the results for
            dataset the latest finalized job will be returned.

        .. seealso::
            :meth:`Beaker.job.results() <JobClient.results>`

        :param experiment: The experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to fetch results for. Required if there are multiple tasks in the experiment.

        :raises ValueError: The experiment has no tasks, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        exp = self.resolve_experiment(experiment)
        job = self.latest_job(exp, task=task, ensure_finalized=True)
        if job is None:
            return None
        else:
            return self.beaker.job.results(job)

    def wait_for(
        self,
        *experiments: Union[str, Experiment],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0,
        quiet: bool = False,
        strict: bool = False,
    ) -> List[Experiment]:
        """
        Wait for experiments to finalize, returning the completed experiments as a list
        in the same order they were given as input.

        .. caution::
            This method is experimental and may change or be removed in future releases.

        .. seealso::
            :meth:`as_completed()`

        .. seealso::
            :meth:`follow()`

        .. seealso::
            :meth:`Beaker.job.wait_for() <JobClient.wait_for>`

        :param experiments: Experiment ID, name, or object.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param poll_interval: Time to wait between polling the experiment (in seconds).
        :param quiet: If ``True``, progress won't be displayed.
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.

        :raises ExperimentNotFound: If any experiment can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises DuplicateExperimentError: If the same experiment is given as an argument more than once.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises TaskStoppedError: If ``strict=True`` and a task is stopped
            before a corresponding job is initialized.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        exp_id_to_position: Dict[str, int] = {}
        exps_to_wait_on: List[Experiment] = []
        for i, exp_ in enumerate(experiments):
            exp = exp_ if isinstance(exp_, Experiment) else self.get(exp_)
            exps_to_wait_on.append(exp)
            if exp.id in exp_id_to_position:
                raise DuplicateExperimentError(exp.display_name)
            exp_id_to_position[exp.id] = i
        completed_exps: List[Experiment] = list(
            self.as_completed(
                *exps_to_wait_on,
                timeout=timeout,
                poll_interval=poll_interval,
                quiet=quiet,
                strict=strict,
            )
        )
        return sorted(completed_exps, key=lambda exp: exp_id_to_position[exp.id])

    def as_completed(
        self,
        *experiments: Union[str, Experiment],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0,
        quiet: bool = False,
        strict: bool = False,
    ) -> Generator[Experiment, None, None]:
        """
        Wait for experiments to finalize, returning an iterator that yields experiments as they
        complete.

        .. caution::
            This method is experimental and may change or be removed in future releases.

        .. seealso::
            :meth:`wait_for()`

        .. seealso::
            :meth:`follow()`

        .. seealso::
            :meth:`Beaker.job.as_completed() <JobClient.as_completed>`

        :param experiments: Experiment ID, name, or object.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param poll_interval: Time to wait between polling the experiment (in seconds).
        :param quiet: If ``True``, progress won't be displayed.
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.

        :raises ExperimentNotFound: If any experiment can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises DuplicateExperimentError: If the same experiment is given as an argument more than once.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises TaskStoppedError: If ``strict=True`` and a task is stopped
            before a corresponding job is initialized.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.monotonic()
        # Initialize progress trackers.
        live_display, experiments_progress, jobs_progress = get_exps_and_jobs_progress(quiet)
        # Keeps track of the IDs of each job for each task in each experiment.
        exp_to_task_to_job: Dict[str, Dict[str, Optional[str]]] = {}
        # Keeps track of the progress tracker "TaskID"s for each experiment.
        exp_to_progress_task: Dict[str, "TaskID"] = {}
        # Keeps track of experiments that haven't been returned yet.
        incomplete_exps: Set[str] = set()
        # Keeps track of jobs that have been finalized.
        finalized_jobs: Set[str] = set()
        # Keeps track of tasks that were stopped before a job was created.
        stopped_tasks: Set[str] = set()

        def num_completed_tasks(exp_id: str) -> int:
            return len(
                [
                    job_id
                    for _, job_id in exp_to_task_to_job[exp_id].items()
                    if job_id is not None and job_id in finalized_jobs
                ]
            )

        def num_stopped_tasks(exp_id: str) -> int:
            return len(
                [
                    task_id
                    for task_id in exp_to_task_to_job[exp_id].keys()
                    if task_id in stopped_tasks
                ]
            )

        def total_tasks(exp_id: str) -> int:
            return len(exp_to_task_to_job[exp_id])

        def experiment_finalized(exp_id: str) -> bool:
            return (num_stopped_tasks(exp_id) + num_completed_tasks(exp_id)) == total_tasks(exp_id)

        def complete_experiment(exp_id: str) -> Experiment:
            incomplete_exps.remove(exp_id)
            experiments_progress.update(exp_to_progress_task[exp_id], completed=total_tasks(exp_id))
            return self.get(exp_id)

        with live_display:
            # Populate progress trackers and state variables, also yielding
            # any experiments that are already complete.
            for e in experiments:
                experiment = self.get(e.id if isinstance(e, Experiment) else e)
                exp_id = experiment.id
                incomplete_exps.add(exp_id)

                # Ensure experiment is unique.
                if exp_id in exp_to_task_to_job:
                    raise DuplicateExperimentError(experiment.display_name)

                # Get state of experiment.
                exp_to_task_to_job[exp_id] = {}
                tasks = self.tasks(experiment)
                for task in tasks:
                    latest_job = self._latest_job(task.jobs)
                    exp_to_task_to_job[exp_id][task.id] = (
                        None if latest_job is None else latest_job.id
                    )
                    if not task.jobs and not task.schedulable:
                        stopped_tasks.add(task.id)

                # Add to progress tracker.
                exp_to_progress_task[exp_id] = experiments_progress.add_task(
                    experiment.display_name,
                    total=total_tasks(exp_id),
                )

            # Now wait for the incomplete experiments to finalize.
            while incomplete_exps:
                # Collect (registered) incomplete jobs and also yield any experiments
                # that have been finalized or stopped.
                incomplete_jobs: List[str] = []
                for exp_id, task_to_job in exp_to_task_to_job.items():
                    if exp_id in incomplete_exps:
                        if strict:
                            for task_id in task_to_job:
                                if task_id in stopped_tasks:
                                    raise TaskStoppedError(task_id)
                        if not experiment_finalized(exp_id):
                            for task_id, job_id in task_to_job.items():
                                if job_id is not None and job_id not in finalized_jobs:
                                    incomplete_jobs.append(job_id)
                        else:
                            # Experiment has just completed, yield it.
                            yield complete_experiment(exp_id)

                # Check for timeout.
                elapsed = time.monotonic() - start
                if timeout is not None and elapsed >= timeout:
                    raise JobTimeoutError

                if incomplete_jobs:
                    # Wait for current stack of incomplete jobs to finalize.
                    for job in self.beaker.job._as_completed(
                        *incomplete_jobs,
                        timeout=None if timeout is None else timeout - elapsed,
                        poll_interval=poll_interval,
                        quiet=quiet,
                        _progress=jobs_progress,
                    ):
                        assert job.execution is not None
                        exp_id = job.execution.experiment
                        task_id = job.execution.task

                        if job.was_preempted:
                            # Job was preempted. Another job will start soon so we just stop
                            # tracking this one.
                            exp_to_task_to_job[exp_id][task_id] = None
                        else:
                            finalized_jobs.add(job.id)

                            # Ensure job was successful if `strict==True`.
                            if strict:
                                job.check()

                            # Update progress display.
                            experiments_progress.advance(exp_to_progress_task[exp_id])

                            # Check if corresponding experiment is now finalized.
                            if experiment_finalized(exp_id) and exp_id in incomplete_exps:
                                # Experiment has just completed, yield it.
                                yield complete_experiment(exp_id)
                else:
                    # Wait for `poll_interval` to give Beaker a chance to register jobs.
                    time.sleep(poll_interval)

                # Now check for jobs that haven't been registered yet.
                for exp_id, task_to_job in exp_to_task_to_job.items():
                    if experiment_finalized(exp_id):
                        # Experiment already finalized, no need for anything.
                        continue

                    if all(job_id is not None for job_id in task_to_job.values()):
                        # All tasks already have registered jobs.
                        continue

                    for task in self.tasks(exp_id):
                        if task_to_job[task.id] is not None:
                            continue

                        if not task.jobs and not task.schedulable:
                            # Task was stopped before a job was created.
                            stopped_tasks.add(task.id)
                        elif task.jobs:
                            latest_job = self._latest_job(task.jobs)
                            assert latest_job is not None
                            task_to_job[task.id] = latest_job.id

    def follow(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        timeout: Optional[float] = None,
        strict: bool = False,
        include_timestamps: bool = True,
        since: Optional[Union[str, datetime, timedelta]] = None,
    ) -> Generator[bytes, None, Experiment]:
        """
        Follow an experiment live, creating a generator that produces log lines
        (as bytes) from the task's job as they become available.
        The return value of the generator is the final
        :class:`~beaker.data_model.experiment.Experiment` object.

        .. seealso::
            :meth:`follow_structured()`

        .. seealso::
            :meth:`logs()`

        .. seealso::
            :meth:`wait_for()`

        .. seealso::
            :meth:`as_completed()`

        .. seealso::
            :meth:`Beaker.job.follow() <JobClient.follow>`

        :param experiment: Experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to follow. Required if there are multiple tasks in the experiment.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param strict: If ``True``, the exit code of the job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.
        :param include_timestamps: If ``True`` (the default) timestamps from the Beaker logs
            will be included in the output.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC), a timestamp string in the form of RFC 3339
            (e.g. "2013-01-02T13:23:37Z"), or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).

        :raises ExperimentNotFound: If any experiment can't be found.
        :raises ValueError: The experiment has no tasks or jobs, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises JobFailedError: If ``strict=True`` and the task's job finishes with a non-zero exit code.
        :raises TaskStoppedError: If ``strict=True`` and a task is stopped
            before a corresponding job is initialized.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

        :examples:

        >>> for line in beaker.experiment.follow(hello_world_experiment_name):
        ...     # Every log line from Beaker starts with an RFC 3339 UTC timestamp
        ...     # (e.g. '2021-12-07T19:30:24.637600011Z'). If we don't want to print
        ...     # the timestamps we can split them off like this:
        ...     line = line[line.find(b"Z ")+2:]
        ...     print(line.decode(errors="ignore"), end="")
        <BLANKLINE>
        Hello from Docker!
        This message shows that your installation appears to be working correctly.
        <BLANKLINE>
        ...
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.monotonic()
        job: Optional[Job] = None
        while job is None:
            actual_task = self._task(experiment, task=task)
            if actual_task.jobs:
                job = self.latest_job(experiment, task=actual_task)
            elif not actual_task.schedulable:
                if strict:
                    raise TaskStoppedError(
                        task.id if isinstance(task, Task) else task, task=actual_task
                    )
                else:
                    return self.get(
                        experiment.id if isinstance(experiment, Experiment) else experiment
                    )

            if timeout is not None and time.monotonic() - start >= timeout:
                raise JobTimeoutError(
                    "Job for task failed to initialize within '{timeout}' seconds"
                )
            time.sleep(2.0)

        assert job is not None
        yield from self.beaker.job.follow(
            job,
            timeout=None if timeout is None else max(timeout - (time.monotonic() - start), 1.0),
            strict=strict,
            include_timestamps=include_timestamps,
            since=since,
        )
        return self.get(experiment.id if isinstance(experiment, Experiment) else experiment)

    def follow_structured(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        timeout: Optional[float] = None,
        strict: bool = False,
        since: Optional[Union[datetime, timedelta]] = None,
        tail_lines: Optional[int] = None,
    ) -> Generator[JobLog, None, Experiment]:
        """
        Follow structured :class:`~beaker.data_model.job.JobLog` objects from a job
        in an experiment using the RPC interface.
        The return value of the generator is the finalized :class:`~beaker.data_model.experiment.Experiment`
        object.

        .. seealso::
            :meth:`follow()`

        .. seealso::
            :meth:`Beaker.job.follow_structured() <JobClient.follow_structured>`

        :param experiment: Experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to follow. Required if there are multiple tasks in the experiment.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC) or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).
        :param tail_lines: Start tailing with the last ``tail_lines`` lines.

        :raises ExperimentNotFound: If any experiment can't be found.
        :raises ValueError: The experiment has no tasks or jobs, or the experiment has multiple tasks but
            ``task`` is not specified.
        :raises TaskNotFound: If the given task doesn't exist.
        :raises TaskStoppedError: If ``strict=True`` and a task is stopped
            before a corresponding job is initialized.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises RpcError: Any other RPC error.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.monotonic()
        job: Optional[Job] = None
        while job is None:
            actual_task = self._task(experiment, task=task)
            if actual_task.jobs:
                job = self.latest_job(experiment, task=actual_task)
            elif not actual_task.schedulable:
                if strict:
                    raise TaskStoppedError(
                        task.id if isinstance(task, Task) else task, task=actual_task
                    )
                else:
                    return self.get(
                        experiment.id if isinstance(experiment, Experiment) else experiment
                    )

            if timeout is not None and time.monotonic() - start >= timeout:
                raise JobTimeoutError(
                    "Job for task failed to initialize within '{timeout}' seconds"
                )
            time.sleep(2.0)

        assert job is not None
        yield from self.beaker.job.follow_structured(
            job,
            timeout=None if timeout is None else max(timeout - (time.monotonic() - start), 1.0),
            strict=strict,
            since=since,
            tail_lines=tail_lines,
        )

        return self.get(experiment.id if isinstance(experiment, Experiment) else experiment)

    def url(
        self, experiment: Union[str, Experiment], task: Optional[Union[str, Task]] = None
    ) -> str:
        """
        Get the URL for an experiment.

        :param experiment: The experiment ID, name, or object.
        :param task: The task ID, name, or object of a specific task from the Beaker experiment
            to get the url for.

        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        experiment = self.resolve_experiment(experiment)
        experiment_url = f"{self.config.agent_address}/ex/{self.url_quote(experiment.id)}"
        if task is None:
            return experiment_url
        else:
            task_id: str
            if isinstance(task, Task):
                task_id = task.id
            else:
                for t in self.tasks(experiment):
                    if t.name == task or t.id == task:
                        task_id = t.id
                        break
                else:
                    raise TaskNotFound(f"No task '{task}' in experiment {experiment.id}")
            return f"{experiment_url}/tasks/{task_id}"

    def latest_job(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        ensure_finalized: bool = False,
        strict: bool = True,
    ) -> Optional[Job]:
        """
        Get the latest job that ran for a task in an experiment.

        .. seealso::
            :meth:`all_latest_jobs()`

        :param experiment: The experiment ID, name, or object.
        :param task: The take ID, name, or object.
        :param ensure_finalized: Consider only finalized jobs.
        :param strict: If ``True``, a ``ValueError`` is raised when ``task`` isn't specified
            and the experiment has multiple tasks.

        :raises ValueError: The experiment has no tasks, or the experiment has multiple tasks but
            ``task`` is not specified and ``strict=True`` (the default).
        :raises TaskNotFound: If the given task doesn't exist.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return self._latest_job(
            self._task(experiment, task, strict=strict).jobs, ensure_finalized=ensure_finalized
        )

    def all_latest_jobs(
        self, experiment: Union[str, Experiment], ensure_finalized: bool = False
    ) -> List[Optional[Job]]:
        """
        Get the latest job for each task in the experiment.

        .. seealso::
            :meth:`latest_job()`

        :param experiment: The experiment ID, name, or object.
        :param ensure_finalized: Consider only finalized jobs.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        jobs: List[Optional[Job]] = []
        for task in self.tasks(experiment):
            jobs.append(self.latest_job(experiment, task=task, ensure_finalized=ensure_finalized))
        return jobs

    def _task(
        self,
        experiment: Union[str, Experiment],
        task: Optional[Union[str, Task]] = None,
        strict: bool = True,
    ) -> Task:
        tasks = list(self.tasks(experiment))
        exp_id = experiment if isinstance(experiment, str) else experiment.id

        if not tasks:
            raise ValueError(f"Experiment '{exp_id}' has no tasks")
        else:
            if task is None:
                if len(tasks) == 1 or not strict:
                    return tasks[0]
                else:
                    raise ValueError(
                        f"'task' required since experiment '{exp_id}' has multiple tasks"
                    )
            else:
                task_name_or_id = task.id if isinstance(task, Task) else task
                tasks = [t for t in tasks if t.name == task_name_or_id or t.id == task_name_or_id]
                if tasks:
                    return tasks[0]
                else:
                    raise TaskNotFound(f"No task '{task_name_or_id}' in experiment '{exp_id}'")

    def _not_found_err_msg(self, experiment: Union[str, Experiment]) -> str:
        experiment = experiment if isinstance(experiment, str) else experiment.id
        return (
            f"'{experiment}': Make sure you're using a valid Beaker experiment ID or the "
            f"*full* name of the experiment (with the account prefix, e.g. 'username/experiment_name')"
        )

    def _validate_spec(self, spec: ExperimentSpec, workspace: Workspace) -> None:
        for task in spec.tasks:
            # Make sure image exists.
            if task.image.beaker is not None:
                self.beaker.image.get(task.image.beaker)
            # Make sure all beaker data sources exist.
            for data_mount in task.datasets or []:
                source = data_mount.source
                if source.beaker is not None:
                    self.beaker.dataset.get(source.beaker)
                if source.secret is not None:
                    self.beaker.secret.get(source.secret, workspace=workspace)
                if source.result is not None:
                    if source.result not in {t.name for t in spec.tasks}:
                        raise ValueError(
                            f"Data mount result source '{source.result}' not found in spec"
                        )
            # Make sure secrets in env variables exist.
            for env_var in task.env_vars or []:
                if env_var.secret is not None:
                    self.beaker.secret.get(env_var.secret, workspace=workspace)
            # Make sure cluster exists.
            if task.context.cluster:
                self.beaker.cluster.get(task.context.cluster)

    def _latest_job(self, jobs: Sequence[Job], ensure_finalized: bool = False) -> Optional[Job]:
        if ensure_finalized:
            jobs = [
                job
                for job in jobs
                if job.status.current == CurrentJobStatus.finalized and job.execution is not None
            ]
        if not jobs:
            return None
        return sorted(jobs, key=lambda job: job.status.created)[-1]
