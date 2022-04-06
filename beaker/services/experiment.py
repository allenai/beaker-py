import time
from typing import Any, Dict, Generator, Union

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class ExperimentClient(ServiceClient):
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

        :raises ExperimentConflict: If an experiment with the given name already exists.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        json_spec: Dict[str, Any]
        if isinstance(spec, ExperimentSpec):
            json_spec = spec.to_json()
        else:
            import yaml

            with open(spec) as spec_file:
                raw_spec = yaml.load(spec_file, Loader=yaml.SafeLoader)
                spec = ExperimentSpec.from_json(raw_spec)
                json_spec = spec.to_json()

        workspace_name = self._resolve_workspace(workspace)
        experiment_data = self.request(
            f"workspaces/{self._url_quote(workspace_name)}/experiments",
            method="POST",
            query={"name": name},
            data=json_spec,
            exceptions_for_status={409: ExperimentConflict(name)},
        ).json()
        return self.get(experiment_data["id"])

    def get(self, experiment: str) -> Experiment:
        """
        Get info about an experiment.

        :param experiment: The experiment ID or full name.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        return Experiment.from_json(
            self.request(
                f"experiments/{self._url_quote(experiment)}",
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment))
                },
            ).json()
        )

    def delete(self, experiment: Union[str, Experiment]):
        """
        Delete an experiment.

        :param experiment: The experiment ID, full name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = experiment if isinstance(experiment, str) else experiment.id
        self.request(
            f"experiments/{self._url_quote(experiment_id)}",
            method="DELETE",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment_id))},
        )

    def list(self, workspace: Optional[str] = None) -> List[Experiment]:
        """
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return [
            Experiment.from_json(d)
            for d in self.request(
                f"workspaces/{self._url_quote(workspace_name)}/experiments",
                exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
            ).json()["data"]
        ]

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

        :param experiment: The experiment ID, full name, or object.
        :param job_id: The ID of a specific job from the Beaker experiment to get the logs for.
            Required if there are more than one jobs in the experiment.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        exp = self.get(experiment if isinstance(experiment, str) else experiment.id)
        if job_id is None:
            if len(exp.jobs) > 1:
                raise ValueError(
                    f"Experiment {exp.id} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp.jobs[0].id
        return self.beaker.job.logs(job_id, quiet=quiet)

    def await_all(
        self,
        experiment: Union[str, Experiment],
        timeout: Optional[int] = None,
        poll_interval: float = 2.0,
        quiet: bool = False,
    ) -> Experiment:
        """
        Wait for all jobs in an experiment to complete.

        :param experiment: The experiment ID, full name, or object.
        :param timeout: Maximum amount of time to wait for (in seocnds).
        :param poll_interval: Time to wait between polling the experiment (in seconds).
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises TimeoutError: If the ``timeout`` expires.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        start = time.time()
        with Progress(
            "[progress.description]{task.description}",
            SpinnerColumn(),
            TimeElapsedColumn(),
            disable=quiet,
        ) as progress:
            task_id = progress.add_task(f"Waiting on {experiment}:")
            polls = 0
            while True:
                exp = self.get(experiment if isinstance(experiment, str) else experiment.id)
                if exp.executions:
                    for execution in exp.executions:
                        if execution.state.exit_code is None:
                            break
                    else:
                        return exp
                if timeout is not None and time.time() - start >= timeout:
                    raise TimeoutError
                polls += 1
                progress.update(task_id, total=polls + 1, advance=1)
                time.sleep(poll_interval)

    def _not_found_err_msg(self, experiment: str) -> str:
        return (
            f"'{experiment}': Make sure you're using a valid Beaker experiment ID or the "
            f"*full* name of the experiment (with the account prefix, e.g. 'username/experiment_name')"
        )
