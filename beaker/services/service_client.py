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

    def _resolve_workspace_name(self, workspace: Optional[str]) -> str:
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise WorkspaceNotSet("'workspace' argument required since default workspace not set")
        elif "/" not in workspace_name:
            if self.config.default_org is not None:
                self._validate_workspace_name(workspace_name)
                return f"{self.config.default_org}/{workspace_name}"
            else:
                raise OrganizationNotSet(
                    f"No default organization set and workspace name doesn't include "
                    f"an organization ('{workspace_name}')"
                )
        else:
            org, name = workspace_name.split("/")
            self._validate_workspace_name(name)
            self.beaker.organization.get(org)
            return workspace_name

    def _resolve_workspace(
        self, workspace: Optional[Union[str, Workspace]], read_only_ok: bool = False
    ) -> Workspace:
        out: Workspace
        if isinstance(workspace, Workspace):
            out = workspace
        else:
            workspace_name = self._resolve_workspace_name(workspace)
            out = self.beaker.workspace.get(workspace_name)
        if not read_only_ok and out.archived:
            raise WorkspaceWriteError(f"Workspace {out.full_name} has been archived")
        return out

    def _resolve_org_name(self, org: Optional[str]) -> str:
        org_name = org or self.config.default_org
        if org_name is None:
            raise OrganizationNotSet("'org' argument required since default org name not set")
        return org_name

    def _resolve_org(self, org: Optional[Union[str, Organization]]) -> Organization:
        if isinstance(org, Organization):
            return org
        else:
            org_name = self._resolve_org_name(org)
            return self.beaker.organization.get(org_name)

    def _url_quote(self, id: str) -> str:
        return urllib.parse.quote(id, safe="")

    def _validate_workspace_name(self, name: str):
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"Workspace name can only contain letters, digits, dashes, and underscores: '{name}'"
            )
