import json
import os
import urllib.parse
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

import docker
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

from .config import Config
from .exceptions import *
from .version import VERSION

__all__ = ["Beaker"]


PathOrStr = Union[os.PathLike, Path]


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.
    """

    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(self, config: Config):
        self.config = config
        self.base_url = f"{self.config.agent_address}/api/{self.API_VERSION}"
        self._docker: Optional[docker.DockerClient] = None

    @property
    def user(self) -> str:
        """
        The username associated with this account.
        """
        return self.whoami()["name"]

    @classmethod
    def from_env(cls, **overrides) -> "Beaker":
        """
        Initialize client from a config file and/or environment variables.
        """
        return cls(Config.from_env(**overrides))

    @property
    def docker(self) -> docker.DockerClient:
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
        session.mount(self.base_url, HTTPAdapter(max_retries=retries))
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
    ) -> requests.Response:
        with self._session_with_backoff() as session:
            url = f"{base_url or self.base_url}/{resource}"
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
            )
            if exceptions_for_status is not None and response.status_code in exceptions_for_status:
                raise exceptions_for_status[response.status_code]
            response.raise_for_status()
            return response

    def whoami(self) -> Dict[str, Any]:
        """
        Check who you are authenticated as.
        """
        return self.request("user").json()

    def get_workspace(self, workspace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about the workspace.

        Raises
        ------
        WorkspaceNotFound
        HTTPError

        """
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise ValueError("'workspace' argument required")
        return self.request(
            f"workspaces/{urllib.parse.quote(workspace_name, safe='')}",
            exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
        ).json()

    def ensure_workspace(self, workspace: str):
        """
        Ensure the given workspace exists.

        Raises
        ------
        HTTPError
        ValueError
            If the workspace name is invalid.

        """
        try:
            self.get_workspace(workspace)
        except WorkspaceNotFound:
            org, name = workspace.split("/")
            self.request("workspaces", method="POST", data={"name": name, "org": org})

    def get_experiment(self, exp_id: str) -> Dict[str, Any]:
        """
        Get info about an experiment.

        Raises
        ------
        ExperimentNotFound
        HTTPError

        """
        return self.request(
            f"experiments/{urllib.parse.quote(exp_id, safe='')}",
            exceptions_for_status={404: ExperimentNotFound(exp_id)},
        ).json()

    def create_experiment(
        self, name: str, spec: Dict[str, Any], workspace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Beaker experiment with the given ``spec``.

        Raises
        ------
        ExperimentConflict
        HTTPError

        """
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise ValueError("'workspace' argument required")
        # Ensure workspace exists.
        self.ensure_workspace(workspace_name)
        return self.request(
            f"workspaces/{urllib.parse.quote(workspace_name, safe='')}/experiments",
            method="POST",
            query={"name": name},
            data=spec,
            exceptions_for_status={409: ExperimentConflict(name)},
        ).json()

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get info about a dataset.

        Raises
        ------
        DatasetNotFound
        HTTPError

        """
        return self.request(
            f"datasets/{urllib.parse.quote(dataset_id, safe='')}",
            exceptions_for_status={404: DatasetNotFound(dataset_id)},
        ).json()

    def delete_dataset(self, dataset_id: str):
        self.request(
            f"datasets/{urllib.parse.quote(dataset_id, safe='')}",
            method="DELETE",
            exceptions_for_status={404: DatasetNotFound(dataset_id)},
        )

    def create_dataset(
        self,
        name: str,
        source: PathOrStr,
        target: Optional[str] = None,
        workspace: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a dataset with the source file(s).
        """
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise ValueError("'workspace' argument required")

        # Ensure workspace exists.
        self.ensure_workspace(workspace_name)

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
        return self.request(
            f"datasets/{dataset_info['id']}",
            method="PATCH",
            data={"commit": True},
        ).json()

    def get_logs(self, job_id: str) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.

        Raises
        ------
        JobNotFound
        HTTPError

        """
        response = self.request(
            f"jobs/{job_id}/logs", exceptions_for_status={404: JobNotFound(job_id)}
        )
        content_length = response.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        progress = tqdm(
            unit="iB", unit_scale=True, unit_divisor=1024, total=total, desc="downloading logs"
        )
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                yield chunk

    def get_logs_for_experiment(
        self, exp_id: str, job_id: Optional[str] = None
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Raises
        ------
        ExperimentNotFound
        JobNotFound
        HTTPError

        """
        exp = self.get_experiment(exp_id)
        if job_id is None:
            if len(exp["jobs"]) > 1:
                raise ValueError(
                    f"Experiment {exp_id} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp["jobs"][0]["id"]
        return self.get_logs(job_id)

    def get_image(self, image: str) -> Dict[str, Any]:
        """
        Get info about an image.

        Raises
        ------
        ImageNotFound
        HTTPError

        """
        return self.request(
            f"images/{urllib.parse.quote(image, safe='')}",
            exceptions_for_status={404: ImageNotFound(image)},
        ).json()

    def create_image(
        self, name: str, image_tag: str, workspace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a Docker image to Beaker.

        Raises
        ------
        ImageConflict
        HTTPError

        """
        workspace = workspace or self.config.default_workspace
        if workspace is None:
            raise ValueError("'workspace' argument required")

        # Ensure workspace exists.
        self.ensure_workspace(workspace)

        # Get local Docker image object.
        image = self.docker.images.get(image_tag)

        # Create new image on Beaker.
        image_data = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace, "ImageID": image.id, "ImageTag": image_tag},
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
        with tqdm(
            self.docker.api.push(
                repo_data["imageTag"],
                stream=True,
                decode=True,
                auth_config={
                    "username": auth["user"],
                    "password": auth["password"],
                    "server_address": auth["server_address"],
                },
            ),
            desc="Pushing image",
            bar_format="{desc}: {elapsed}{postfix}",
        ) as pbar:
            for line in pbar:
                if "id" in line:
                    pbar.set_postfix(OrderedDict([("id", line["id"]), ("status", line["status"])]))

        # Commit changes to Beaker.
        self.request(f"images/{image_data['id']}", method="PATCH", data={"Commit": True})

        # Return info about the Beaker image.
        return self.get_image(image_data["id"])

    def delete_image(self, image_id: str):
        """
        Delete an image.

        Raises
        ------
        ImageNotFound
        HTTPError

        """
        self.request(
            f"images/{image_id}",
            method="DELETE",
            exceptions_for_status={404: ImageNotFound(image_id)},
        )

    def list_experiments(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise ValueError("'workspace' argument required")
        return self.request(
            f"workspaces/{urllib.parse.quote(workspace_name, safe='')}/experiments",
            exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
        ).json()["data"]
