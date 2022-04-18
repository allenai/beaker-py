import json
import urllib.parse
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Union

import docker
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from beaker.config import Config
from beaker.data_model import *
from beaker.exceptions import *
from beaker.version import VERSION

if TYPE_CHECKING:
    from ..client import Beaker


class ServiceClient:
    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(self, beaker: "Beaker"):
        self.beaker = beaker
        self._base_url = f"{self.config.agent_address}/api/{self.API_VERSION}"

    @property
    def config(self) -> Config:
        return self.beaker.config

    @property
    def docker(self) -> docker.DockerClient:
        return self.beaker.docker

    @contextmanager
    def _session_with_backoff(self) -> Generator[requests.Session, None, None]:
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
        exceptions_for_status: Optional[Dict[int, Exception]] = None,
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
                "User-Agent": f"beaker-py v{VERSION}",
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

    def resolve_cluster_name(self, cluster_name: str) -> str:
        if "/" not in cluster_name:
            if self.config.default_org is not None:
                self.validate_beaker_name(cluster_name)
                return f"{self.config.default_org}/{cluster_name}"
            else:
                raise OrganizationNotSet(
                    f"No default organization set and cluster name doesn't include "
                    f"an organization ('{cluster_name}')"
                )
        else:
            org, name = cluster_name.split("/", 1)
            self.validate_beaker_name(name)
            self.beaker.organization.get(org)
            return cluster_name

    def resolve_cluster(self, cluster: Union[str, Cluster]) -> Cluster:
        if isinstance(cluster, Cluster):
            return cluster
        else:
            return self.beaker.cluster.get(cluster)

    def resolve_workspace_name(self, workspace_name: str) -> str:
        """
        Takes the name of a workspace (possibly non-existent) and returns a valid full name.
        """
        if "/" not in workspace_name:
            if self.config.default_org is not None:
                self.validate_beaker_name(workspace_name)
                return f"{self.config.default_org}/{workspace_name}"
            else:
                raise OrganizationNotSet(
                    f"No default organization set and workspace name doesn't include "
                    f"an organization ('{workspace_name}'). Make sure you're using a valid "
                    f"workspace full name or ID."
                )
        else:
            org, name = workspace_name.split("/", 1)
            self.validate_beaker_name(name)
            self.beaker.organization.get(org)
            return workspace_name

    def resolve_workspace(
        self,
        workspace: Optional[Union[str, Workspace]],
        read_only_ok: bool = False,
    ) -> Workspace:
        out: Workspace
        if isinstance(workspace, Workspace):
            out = workspace
        else:
            out = self.beaker.workspace.get(workspace)

        if not read_only_ok and out.archived:
            raise WorkspaceWriteError(f"Workspace '{out.full_name}' has been archived")

        return out

    def resolve_dataset(self, dataset: Union[str, Dataset]) -> Dataset:
        if isinstance(dataset, Dataset):
            return dataset
        else:
            return self.beaker.dataset.get(dataset)

    def resolve_experiment(self, experiment: Union[str, Experiment]) -> Experiment:
        if isinstance(experiment, Experiment):
            return experiment
        else:
            return self.beaker.experiment.get(experiment)

    def resolve_image(self, image: Union[str, Image]) -> Image:
        if isinstance(image, Image):
            return image
        else:
            return self.beaker.image.get(image)

    def resolve_group(self, group: Union[str, Group]) -> Group:
        if isinstance(group, Group):
            return group
        else:
            return self.beaker.group.get(group)

    def resolve_org(self, org: Optional[Union[str, Organization]]) -> Organization:
        if isinstance(org, Organization):
            return org
        else:
            return self.beaker.organization.get(org)

    def url_quote(self, id: str) -> str:
        return urllib.parse.quote(id, safe="")

    def validate_beaker_name(self, name: str):
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"Invalid name '{name}'. Beaker names can only contain letters, digits, dashes, and underscores."
            )
