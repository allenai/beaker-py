import time
from typing import Any, Callable, Dict, Generator, Tuple, Union

from rich.progress import Progress, TaskID, TimeElapsedColumn

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
        :param name: The new

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
                    404: ExperimentNotFound(self._not_found_err_msg(experiment_id))
                },
            ).json()
        )

    def logs(
        self,
        experiment: Union[str, Experiment],
        job_id: Optional[str] = None,
        quiet: bool = False,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        :param experiment: The experiment ID, name, or object.
        :param job_id: The ID of a specific job from the Beaker experiment to get the logs for.
            Required if there are more than one jobs in the experiment.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        exp = self.resolve_experiment(experiment)
        if job_id is None:
            if len(exp.jobs) > 1:
                raise ValueError(
                    f"Experiment {exp.id} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp.jobs[0].id
        return self.beaker.job.logs(job_id, quiet=quiet)

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

    def results(self, experiment: Union[str, Experiment]) -> List[Tuple[Task, Dataset]]:
        """
        Get the results for the latest job of each task in an experiment.

        :param experiment: The experiment ID, name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        out: List[Tuple[Task, Dataset]] = []
        for task in self.tasks(experiment):
            jobs = [job for job in task.jobs if job.execution is not None]
            if not jobs:
                continue
            latest_job = sorted(jobs, key=lambda job: (job.status.finalized, job.status.created))[
                -1
            ]
            assert latest_job.execution is not None  # for mypy.
            result_dataset = self.beaker.dataset.get(latest_job.execution.result.beaker)
            out.append((task, result_dataset))
        return out

    def await_all(
        self,
        *experiments: Union[str, Experiment],
        timeout: Optional[int] = None,
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
        finished: Dict[str, Experiment] = {}
        exp_ids: List[str] = [self.resolve_experiment(experiment).id for experiment in experiments]
        start = time.time()
        with Progress(
            "[progress.description]{task.description}", TimeElapsedColumn(), disable=quiet
        ) as progress:
            exp_id_to_task: Dict[str, TaskID] = {}
            for exp_id in exp_ids:
                exp_id_to_task[exp_id] = progress.add_task(f"{exp_id} - waiting")

            polls = 0
            while True:
                if not exp_id_to_task:
                    break

                polls += 1

                # Poll each experiment and update the progress line.
                for exp_id in list(exp_id_to_task):
                    task_id = exp_id_to_task[exp_id]
                    exp = self.get(exp_id)
                    if exp.jobs:
                        for job in exp.jobs:
                            if job.status.current != CurrentJobStatus.finalized:
                                progress.update(task_id, total=polls + 1, advance=1)
                                break
                        else:
                            finished[exp_id] = exp
                            progress.update(
                                task_id,
                                total=polls + 1,
                                complete=polls + 1,
                                description=f"{exp_id} - completed",
                            )
                            progress.stop_task(task_id)
                            del exp_id_to_task[exp_id]

                elapsed = time.time() - start
                if timeout is not None and elapsed >= timeout:
                    raise TimeoutError
                if callback is not None:
                    callback(elapsed)
                time.sleep(poll_interval)

        return [finished[exp_id] for exp_id in exp_ids]

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
