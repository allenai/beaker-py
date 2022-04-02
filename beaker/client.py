import json
import os
import urllib.parse
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

import docker
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import Config
from .data_model import *
from .exceptions import *
from .version import VERSION

__all__ = ["Beaker"]


PathOrStr = Union[os.PathLike, Path]


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.

    :param config: The Beaker :class:`Config`.

    The easiest way to initialize a Beaker client is with :meth:`.from_env()`.
    """

    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(self, config: Config):
        self._config = config
        self._base_url = f"{self._config.agent_address}/api/{self.API_VERSION}"
        self._docker: Optional[docker.DockerClient] = None
        if self._config.default_workspace is not None:
            self.ensure_workspace(self._config.default_workspace)

    @classmethod
    def from_env(cls, **overrides) -> "Beaker":
        """
        Initialize client from a config file and/or environment variables.

        >>> beaker = Beaker.from_env()
        """
        return cls(Config.from_env(**overrides))

    @property
    def config(self) -> Config:
        """
        The client's :class:`Config`.
        """
        return self._config

    @property
    def user(self) -> str:
        """
        The name of the user associated with this account.
        """
        return self.whoami().name

    @property
    def docker(self) -> docker.DockerClient:
        """
        The :class:`~docker.client.DockerClient`.
        """
        if self._docker is None:
            self._docker = docker.from_env()
        assert self._docker is not None
        return self._docker

    @contextmanager
    def _session_with_backoff(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=self.RECOVERABLE_SERVER_ERROR_CODES,
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        yield session

    def request(
        self,
        resource: str,
        method: str = "GET",
        query: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        exceptions_for_status: Optional[Dict[int, BeakerError]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        stream: bool = False,
    ) -> requests.Response:
        with self._session_with_backoff() as session:
            url = f"{base_url or self._base_url}/{resource}"
            if query is not None:
                url = url + "?" + urllib.parse.urlencode(query)
            default_headers = {
                "Authorization": f"Bearer {token or self.config.user_token}",
                "Content-Type": "application/json",
            }
            if headers is not None:
                default_headers.update(headers)
            response = getattr(session, method.lower())(
                url,
                headers=default_headers,
                data=json.dumps(data) if isinstance(data, dict) else data,
                stream=stream,
            )
            if exceptions_for_status is not None and response.status_code in exceptions_for_status:
                raise exceptions_for_status[response.status_code]
            response.raise_for_status()
            return response

    def whoami(self) -> Account:
        """
        Check who you are authenticated as.
        """
        return Account(**self.request("user").json())

    def get_workspace(self, workspace: Optional[str] = None) -> Workspace:
        """
        Get information about the workspace.

        :param workspace: The workspace name. Defaults to :data:`Config.default_workspace`.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` or :data:`Config.default_workspace` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return Workspace(
            **self.request(
                f"workspaces/{urllib.parse.quote(workspace_name, safe='')}",
                exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
            ).json()
        )

    def ensure_workspace(self, workspace: str):
        """
        Ensure that the given workspace exists.

        :raises HTTPError: Any other HTTP exception that can occur.
        :raises ValueError: If the workspace name is invalid.

        """
        try:
            self.get_workspace(workspace)
        except WorkspaceNotFound:
            try:
                org, name = workspace.split("/")
            except ValueError:
                raise ValueError(f"Invalided workspace name '{workspace}'")
            self.request("workspaces", method="POST", data={"name": name, "org": org})

    def get_experiment(self, experiment: str) -> Experiment:
        """
        Get info about an experiment.

        :param experiment: The experiment ID or full name.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        return Experiment(
            **self.request(
                f"experiments/{urllib.parse.quote(experiment, safe='')}",
                exceptions_for_status={404: ExperimentNotFound(experiment)},
            ).json()
        )

    def create_experiment(
        self, name: str, spec: Dict[str, Any], workspace: Optional[str] = None
    ) -> Experiment:
        """
        Create a new Beaker experiment with the given ``spec``.

        :param spec: A Beaker `experiment spec
            <https://github.com/beaker/docs/blob/main/docs/concept/experiments.md#spec-format>`_
            in the form of a Python dictionary.

        :raises ExperimentConflict: If an experiment with the given name already exists.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` or :data:`Config.default_workspace` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace)
        experiment_data = self.request(
            f"workspaces/{urllib.parse.quote(workspace_name, safe='')}/experiments",
            method="POST",
            query={"name": name},
            data=spec,
            exceptions_for_status={409: ExperimentConflict(name)},
        ).json()
        return self.get_experiment(experiment_data["id"])

    def get_dataset(self, dataset: str) -> Dataset:
        """
        Get info about a dataset.

        :param dataset: The dataset ID or full name.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        return Dataset(
            **self.request(
                f"datasets/{urllib.parse.quote(dataset, safe='')}",
                exceptions_for_status={404: DatasetNotFound(dataset)},
            ).json()
        )

    def create_dataset(
        self,
        name: str,
        source: PathOrStr,
        target: Optional[str] = None,
        workspace: Optional[str] = None,
        force: bool = False,
    ) -> Dataset:
        """
        Create a dataset with the source file(s).

        :param name: The name to assign to the new dataset.
        :param source: The local source file or directory of the dataset.
        :param target: If ``source`` is a file, you can change the name of the file in the dataset
            by specifying ``target``.
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Config.default_workspace` is used.
        :param force: If ``True`` and a dataset by the given name already exists, it will be overwritten.

        .. attention::
            Currently only a single file ``source`` is supported.
            See `issue#39 <https://github.com/allenai/beaker-py/issues/39>`_ for tracking.

        :raises DatasetConflict: If a dataset by that name already exists and ``force=False``.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` or :data:`Config.default_workspace` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self._resolve_workspace(workspace)

        # Ensure source exists.
        source: Path = Path(source)
        if not source.exists():
            raise FileNotFoundError(source)

        if not source.is_file():
            raise NotImplementedError("'create_dataset()' only works for single files so far")

        # Create the dataset.
        def make_dataset() -> Dict[str, Any]:
            return self.request(
                "datasets",
                method="POST",
                query={"name": name},
                data={"workspace": workspace_name, "fileheap": True},
                exceptions_for_status={409: DatasetConflict(name)},
            ).json()

        try:
            dataset_info = make_dataset()
        except DatasetConflict:
            if force:
                self.delete_dataset(f"{self.user}/{name}")
                dataset_info = make_dataset()
            else:
                raise

        # Upload the file.
        with source.open("rb") as source_file:
            self.request(
                f"datasets/{dataset_info['storage']['id']}/files/{target or source.name}",
                method="PUT",
                data=source_file,
                token=dataset_info["storage"]["token"],
                base_url=dataset_info["storage"]["address"],
                headers={
                    "User-Agent": f"beaker-py v{VERSION}",
                },
            )

        # Commit the dataset.
        self.request(
            f"datasets/{dataset_info['id']}",
            method="PATCH",
            data={"commit": True},
        ).json()

        # Return info about the dataset.
        return self.get_dataset(dataset_info["id"])

    def delete_dataset(self, dataset: str):
        """
        Delete a dataset.

        :param dataset: The dataset ID or full name.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        self.request(
            f"datasets/{urllib.parse.quote(dataset, safe='')}",
            method="DELETE",
            exceptions_for_status={404: DatasetNotFound(dataset)},
        )

    def get_logs(self, job_id: str, quiet: bool = False) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. seealso::
            :meth:`get_logs_for_experiment()`

        :param job_id: The ID of the Beaker job.
        :param quiet: If ``True``, progress won't be displayed.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        from rich.progress import (
            FileSizeColumn,
            Progress,
            SpinnerColumn,
            TimeElapsedColumn,
        )

        response = self.request(
            f"jobs/{job_id}/logs",
            exceptions_for_status={404: JobNotFound(job_id)},
            stream=True,
        )

        # TODO: currently beaker doesn't provide the Content-Length header, update this if they do.
        #  content_length = response.headers.get("Content-Length")
        #  total = int(content_length) if content_length is not None else None

        with Progress(
            "[progress.description]{task.description}",
            SpinnerColumn(),
            FileSizeColumn(),
            TimeElapsedColumn(),
            disable=quiet,
        ) as progress:
            task_id = progress.add_task("Downloading:")
            total = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    advance = len(chunk)
                    total += advance
                    progress.update(task_id, total=total + 1, advance=advance)
                    yield chunk

    def get_logs_for_experiment(
        self,
        experiment: str,
        job_id: Optional[str] = None,
        quiet: bool = False,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        :param experiment: The experiment ID or full name.
        :param job_id: The ID of a specific job from the Beaker experiment to get the logs for.
            Required if there are more than one jobs in the experiment.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        exp = self.get_experiment(experiment)
        if job_id is None:
            if len(exp["jobs"]) > 1:
                raise ValueError(
                    f"Experiment {experiment} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp["jobs"][0]["id"]
        return self.get_logs(job_id, quiet=quiet)

    def get_image(self, image: str) -> Image:
        """
        Get info about an image.

        :param image: The Beaker image ID or full name.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        return Image(
            **self.request(
                f"images/{urllib.parse.quote(image, safe='')}",
                exceptions_for_status={404: ImageNotFound(image)},
            ).json()
        )

    def create_image(
        self,
        name: str,
        image_tag: str,
        workspace: Optional[str] = None,
        quiet: bool = False,
    ) -> Image:
        """
        Upload a Docker image to Beaker.

        :param name: The name to assign to the image on Beaker.
        :param image_tag: The tag of the local image you're uploading.
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Config.default_workspace` is used.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ImageConflict: If an image with the given name already exists.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` or :data:`Config.default_workspace` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace)

        # Get local Docker image object.
        image = self.docker.images.get(image_tag)

        # Create new image on Beaker.
        image_data = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace_name, "ImageID": image.id, "ImageTag": image_tag},
            query={"name": name},
            exceptions_for_status={409: ImageConflict(name)},
        ).json()

        # Get the repo data for the Beaker image.
        repo_data = self.request(
            f"images/{image_data['id']}/repository", query={"upload": True}
        ).json()
        auth = repo_data["auth"]

        # Tag the local image with the new tag for the Beaker image.
        image.tag(repo_data["imageTag"])

        # Push the image to Beaker.
        from rich.progress import BarColumn, Progress, TimeRemainingColumn

        from .util import DownloadUploadColumn

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            DownloadUploadColumn(),
            disable=quiet,
        ) as progress:
            layer_id_to_task: Dict[str, str] = {}
            for line in self.docker.api.push(
                repo_data["imageTag"],
                stream=True,
                decode=True,
                auth_config={
                    "username": auth["user"],
                    "password": auth["password"],
                    "server_address": auth["server_address"],
                },
            ):
                if "id" not in line or "status" not in line:
                    continue
                layer_id = line["id"]
                status = line["status"].lower()
                progress_detail = line.get("progressDetail")
                task_id: str
                if layer_id not in layer_id_to_task:
                    task_id = progress.add_task(layer_id, start=True, total=1)
                    layer_id_to_task[layer_id] = task_id
                else:
                    task_id = layer_id_to_task[layer_id]
                if status in {"preparing", "waiting"}:
                    progress.update(
                        task_id, total=1, completed=0, description=f"{layer_id}: {status.title()}"
                    )
                elif status == "pushing" and progress_detail:
                    progress.update(
                        task_id,
                        total=progress_detail["total"],
                        completed=progress_detail["current"],
                        description=f"{layer_id}: Pushing",
                    )
                elif status == "pushed":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Push complete"
                    )
                elif status == "layer already exists":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Already exists"
                    )
                else:
                    raise ValueError(f"unhandled status '{status}' ({line})")

        # Commit changes to Beaker.
        self.request(f"images/{image_data['id']}", method="PATCH", data={"Commit": True})

        # Return info about the Beaker image.
        return self.get_image(image_data["id"])

    def delete_image(self, image: str):
        """
        Delete an image.

        :param image: The Beaker image ID or full name.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        self.request(
            f"images/{urllib.parse.quote(image, safe='')}",
            method="DELETE",
            exceptions_for_status={404: ImageNotFound(image)},
        )

    def list_experiments(self, workspace: Optional[str] = None) -> List[Experiment]:
        """
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Config.default_workspace` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` or :data:`Config.default_workspace` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return [
            Experiment(**d)
            for d in self.request(
                f"workspaces/{urllib.parse.quote(workspace_name, safe='')}/experiments",
                exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
            ).json()["data"]
        ]

    def _resolve_workspace(self, workspace: Optional[str], ensure_exists: bool = True) -> str:
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise WorkspaceNotSet("'workspace' argument required since default workspace not set")
        else:
            if ensure_exists:
                self.ensure_workspace(workspace_name)
            return workspace_name
