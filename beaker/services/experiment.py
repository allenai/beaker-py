import time
from typing import Any, Callable, Dict, Generator, Union

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


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
        :raises HTTPError: Any other HTTP exception that can occur.
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
                # Now try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{experiment}")
                except ExperimentNotFound:
                    pass
            raise

    def create(
        self, name: str, spec: Union[ExperimentSpec, PathOrStr], workspace: Optional[str] = None
    ) -> Experiment:
        """
        Create a new Beaker experiment with the given ``spec``.

        :param name: The name to assign the experiment.
        :param spec: The spec for the Beaker experiment. This can either be an
            :class:`~beaker.data_model.ExperimentSpec` instance or the path to a YAML spec file.
        :param workspace: The workspace to create the experiment under. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises ValueError: If the name is invalid.
        :raises ExperimentConflict: If an experiment with the given name already exists.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        self.validate_beaker_name(name)
        json_spec: Dict[str, Any]
        if isinstance(spec, ExperimentSpec):
            json_spec = spec.to_json()
        else:
            spec = ExperimentSpec.from_file(spec)
            json_spec = spec.to_json()
        workspace: Workspace = self.resolve_workspace(workspace)
        self._validate_spec(spec, workspace)
        experiment_data = self.request(
            f"workspaces/{workspace.id}/experiments",
            method="POST",
            query={"name": name},
            data=json_spec,
            exceptions_for_status={409: ExperimentConflict(name)},
        ).json()
        return self.get(experiment_data["id"])

    def spec(self, experiment: Union[str, Experiment]) -> ExperimentSpec:
        """
        Get the :class:`spec <beaker.data_model.ExperimentSpec>` of an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = self.resolve_experiment(experiment).id
        return ExperimentSpec.from_json(
            self.request(
                f"experiments/{self.url_quote(experiment_id)}/spec",
                query={"version": SPEC_VERSION},
                headers={"Accept": "application/json"},
            ).json()
        )

    def stop(self, experiment: Union[str, Experiment]):
        """
        Stop an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = self.resolve_experiment(experiment).id
        self.request(
            f"experiments/{self.url_quote(experiment_id)}/stop",
            method="PUT",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment_id))},
        )

    def resume(self, experiment: Union[str, Experiment]):
        """
        Resume a preempted experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = self.resolve_experiment(experiment).id
        self.request(
            f"experiments/{self.url_quote(experiment_id)}/resume",
            method="POST",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment_id))},
        )

    def delete(self, experiment: Union[str, Experiment]):
        """
        Delete an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = self.resolve_experiment(experiment).id
        self.request(
            f"experiments/{self.url_quote(experiment_id)}",
            method="DELETE",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment_id))},
        )

    def rename(self, experiment: Union[str, Experiment], name: str) -> Experiment:
        """
        Rename an experiment.

        :param experiment: The experiment ID, name, or object.
        :param name: The new name for the experiment.

        :raises ValueError: If the new name is invalid.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        experiment_id = self.resolve_experiment(experiment).id
        return Experiment.from_json(
            self.request(
                f"experiments/{self.url_quote(experiment_id)}",
                method="PATCH",
                data={"name": name},
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment_id)),
                    409: ExperimentConflict(name),
                },
            ).json()
        )

    def tasks(self, experiment: Union[str, Experiment]) -> List[Task]:
        """
        List the tasks in an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = self.resolve_experiment(experiment).id
        return [
            Task.from_json(d)
            for d in self.request(
                f"experiments/{self.url_quote(experiment_id)}/tasks",
                method="GET",
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment_id))
                },
            ).json()
        ]

    def logs(
        self,
        experiment: Union[str, Experiment],
        task_name: Optional[str] = None,
        quiet: bool = False,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. important::
            When there are multiple jobs for the given experiment / task, the logs for the latest job
            will be returned.

        .. seealso::
            :meth:`Beaker.job.logs() <JobClient.logs>`

        :param experiment: The experiment ID, name, or object.
        :param task_name: The name of the task from the Beaker experiment.
            Required if there are multiple tasks in the experiment.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ValueError: The experiment has no tasks or jobs, or the experiment has multiple tasks but
            ``task_name`` is not specified.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        exp = self.resolve_experiment(experiment)
        job = self._latest_job_for_task(exp, task_name=task_name, ensure_finalized=False)
        if job is None:
            if task_name is None:
                raise ValueError(f"Experiment {exp.id} has no jobs")
            else:
                raise ValueError(f"Experiment {exp.id} has no jobs for task '{task_name}'")
        return self.beaker.job.logs(job.id, quiet=quiet)

    def metrics(
        self, experiment: Union[str, Experiment], task_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the metrics from a task in an experiment.

        .. important::
            When there are multiple jobs for the given experiment / task, the metrics for
            the latest finalized job will be returned.

        .. seealso::
            :meth:`Beaker.job.metrics() <JobClient.metrics>`

        :param experiment: The experiment ID, name, or object.
        :param task_name: The name of the task from the Beaker experiment.
            Required if there are multiple tasks in the experiment.

        :raises ValueError: The experiment has no tasks, or the experiment has multiple tasks but
            ``task_name`` is not specified.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        exp = self.resolve_experiment(experiment)
        job = self._latest_job_for_task(exp, task_name=task_name, ensure_finalized=True)
        return None if job is None else self.beaker.job.metrics(job.id)

    def results(
        self, experiment: Union[str, Experiment], task_name: Optional[str] = None
    ) -> Optional[Dataset]:
        """
        Get the result dataset from a task in an experiment.

        .. important::
            When there are multiple jobs for the given experiment / task, the metrics for
            the latest finalized job will be returned.

        .. seealso::
            :meth:`Beaker.job.results() <JobClient.results>`

        :param experiment: The experiment ID, name, or object.
        :param task_name: The name of the task from the Beaker experiment.
            Required if there are multiple tasks in the experiment.

        :raises ValueError: The experiment has no tasks, or the experiment has multiple tasks but
            ``task_name`` is not specified.
        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        exp = self.resolve_experiment(experiment)
        job = self._latest_job_for_task(exp, task_name=task_name, ensure_finalized=True)
        if job is None:
            return None
        else:
            assert job.execution is not None  # for mypy
            return self.beaker.dataset.get(job.execution.result.beaker)

    def await_all(
        self,
        *experiments: Union[str, Experiment],
        timeout: Optional[float] = None,
        poll_interval: float = 2.0,
        quiet: bool = False,
        callback: Optional[Callable[[float], None]] = None,
    ) -> List[Experiment]:
        """
        Wait for all jobs in the experiments to complete.

        :param experiments: Experiment ID, name, or object.
        :param timeout: Maximum amount of time to wait for (in seocnds).
        :param poll_interval: Time to wait between polling the experiment (in seconds).
        :param quiet: If ``True``, progress won't be displayed.
        :param callback: An optional user-provided callback function that takes a
            single argument - the elapsed time.

        :raises ExperimentNotFound: If any experiment can't be found.
        :raises TimeoutError: If the ``timeout`` expires.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.time()
        job_await_timeout = timeout

        def get_unfinished():
            exps = []
            jobs = []
            for exp_ in experiments:
                experiment = self.get(exp_.id if isinstance(exp_, Experiment) else exp_)
                if experiment.jobs:
                    has_unfinished_jobs = False
                    for job in experiment.jobs:
                        if job.status.current != CurrentJobStatus.finalized:
                            jobs.append(job)
                            has_unfinished_jobs = True
                    if has_unfinished_jobs:
                        exps.append(experiment)
                else:
                    exps.append(experiment)
            return exps, jobs

        exps_to_wait_on, jobs_to_wait_on = get_unfinished()
        while exps_to_wait_on or jobs_to_wait_on:
            elapsed = time.time() - start
            if timeout is not None and elapsed >= timeout:
                raise TimeoutError
            if callback is not None:
                callback(elapsed)

            if jobs_to_wait_on:
                if timeout is not None:
                    job_await_timeout = timeout - elapsed
                self.beaker.job.await_all(
                    *jobs_to_wait_on,
                    timeout=job_await_timeout,
                    poll_interval=poll_interval,
                    quiet=quiet,
                    callback=callback,
                )
            else:
                time.sleep(poll_interval)

            exps_to_wait_on, jobs_to_wait_on = get_unfinished()

        return [self.get(exp.id if isinstance(exp, Experiment) else exp) for exp in experiments]

    def _not_found_err_msg(self, experiment: str) -> str:
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
            self.beaker.cluster.get(task.context.cluster)

    def _latest_job_for_task(
        self,
        experiment: Experiment,
        task_name: Optional[str] = None,
        ensure_finalized: bool = False,
    ) -> Optional[Job]:
        tasks = self.tasks(experiment)

        if not tasks:
            raise ValueError(f"Experiment '{experiment.id}' has no tasks")
        elif len(tasks) > 1:
            if not task_name:
                raise ValueError(
                    f"'task_name' required since experiment '{experiment.id}' has multiple tasks"
                )
            else:
                tasks = [task for task in tasks if task.name == task_name]
                if not tasks:
                    raise ValueError(f"No task named '{task_name}' in experiment '{experiment.id}'")

        task = tasks[0]
        return self._latest_job(task.jobs, ensure_finalized=ensure_finalized)

    def _latest_job(self, jobs: List[Job], ensure_finalized: bool = False) -> Optional[Job]:
        if ensure_finalized:
            jobs = [
                job
                for job in jobs
                if job.status.current == CurrentJobStatus.finalized and job.execution is not None
            ]
        if not jobs:
            return None
        return sorted(jobs, key=lambda job: (job.status.finalized, job.status.created))[-1]
