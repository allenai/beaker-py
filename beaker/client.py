import json
import urllib.parse
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

from .util import run_cmd, stream_cmd


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.
    """

    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(self, token: str):
        self.base_url = f"https://beaker.org/api/{self.API_VERSION}"
        self.token = token

    @classmethod
    def from_env(cls) -> "Beaker":
        """
        Initialize client from environment variables. Expects the beaker auth token
        to be set as the ``BEAKER_TOKEN`` environment variable.
        """
        import os

        token = os.environ["BEAKER_TOKEN"]
        return cls(token)

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
        data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        with self._session_with_backoff() as session:
            url = f"{self.base_url}/{resource}"
            if query is not None:
                url = url + "?" + urllib.parse.urlencode(query)
            response = getattr(session, method.lower())(
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                data=None if data is None else json.dumps(data),
            )
            response.raise_for_status()
            return response

    def whoami(self) -> Dict[str, Any]:
        """
        Check who you are authenticated as.
        """
        return self.request("user").json()

    def experiment(self, exp_id: str) -> Dict[str, Any]:
        """
        Get info about an experiment.
        """
        return self.request(f"experiments/{exp_id}").json()

    def dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get info about a dataset.
        """
        return self.request(f"datasets/{dataset_id}").json()

    def logs(self, job_id: str) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.
        """
        response = self.request(f"jobs/{job_id}/logs")
        content_length = response.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        progress = tqdm(
            unit="iB", unit_scale=True, unit_divisor=1024, total=total, desc="downloading"
        )
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                yield chunk

    def logs_for_experiment(
        self, exp_id: str, job_id: Optional[str] = None
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.
        """
        exp = self.experiment(exp_id)
        if job_id is None:
            if len(exp["jobs"]) > 1:
                raise ValueError(
                    f"Experiment {exp_id} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp["jobs"][0]["id"]
        return self.logs(job_id)

    def create_image(
        self, name: str, workspace: str, image_tag: str, image_digest: str
    ) -> Dict[str, Any]:
        """
        Upload a Docker image to Beaker.
        """
        image_data = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace, "ImageID": image_digest, "ImageTag": image_tag},
            query={"name": name},
        ).json()

        repo_data = self.request(
            f"images/{image_data['id']}/repository", query={"upload": True}
        ).json()
        auth = repo_data["auth"]

        run_cmd(f"docker tag {image_tag} {repo_data['imageTag']}")
        run_cmd(f"docker login -u {auth['user']} -p {auth['password']} {auth['server_address']}")

        for line in stream_cmd(f"docker push {repo_data['imageTag']}"):
            print(line)

        self.request(f"images/{image_data['id']}", method="PATCH", data={"Commit": True})
        return self.request(f"images/{image_data['id']}").json()

    def delete_image(self, image_id: str):
        self.request(f"images/{image_id}", method="DELETE")
