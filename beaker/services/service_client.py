import io
import json
import logging
import urllib.parse
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import docker
import grpc
import requests
from google.protobuf.message import Message

from .. import beaker_pb2 as pb2
from ..config import Config
from ..data_model import *
from ..data_model.base import BaseModel
from ..exceptions import *
from ..util import retriable

if TYPE_CHECKING:
    from ..client import Beaker


T = TypeVar("T")


class ServiceClient:
    def __init__(self, beaker: "Beaker"):
        self.beaker = beaker
        self._base_url = f"{self.config.agent_address}/api/{self.beaker.API_VERSION}"

    @property
    def config(self) -> Config:
        return self.beaker.config

    @property
    def docker(self) -> docker.DockerClient:
        return self.beaker.docker

    @property
    def logger(self) -> logging.Logger:
        return self.beaker.logger

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
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> requests.Response:
        def make_request(session: requests.Session) -> requests.Response:
            # Build URL.
            url = f"{base_url or self._base_url}/{resource}"
            if query is not None:
                url = url + "?" + urllib.parse.urlencode(query)

            # Populate headers.
            default_headers = {
                "Authorization": f"Bearer {token or self.config.user_token}",
                "Content-Type": "application/json",
                "User-Agent": self.beaker.user_agent,
            }
            if headers is not None:
                default_headers.update(headers)

            # Validate request data.
            request_data: Optional[Union[str, bytes, io.BufferedReader]] = None
            if isinstance(data, BaseModel):
                request_data = json.dumps(data.to_json())
            elif isinstance(data, dict):
                request_data = json.dumps(data)
            elif isinstance(data, (str, bytes, io.BufferedReader)):
                request_data = data
            elif data is not None:
                raise TypeError(
                    f"Unexpected type for 'data'. Expected 'dict' or 'BaseModel', got {type(data)}"
                )

            # Log request at DEBUG.
            if isinstance(request_data, str):
                self.logger.debug("SEND %s %s - %s", method, url, request_data)
            elif isinstance(request_data, bytes):
                self.logger.debug("SEND %s %s - %d bytes", method, url, len(request_data))
            elif request_data is not None:
                self.logger.debug("SEND %s %s - ? bytes", method, url)
            else:
                self.logger.debug("SEND %s %s", method, url)

            # Make request.
            response = getattr(session, method.lower())(
                url,
                headers=default_headers,
                data=request_data,
                stream=stream,
                timeout=timeout or self.beaker._timeout,
            )

            # Log response at DEBUG.
            if (
                not stream
                and self.logger.isEnabledFor(logging.DEBUG)
                and len(response.content) < 1024
                and response.text
            ):
                self.logger.debug("RECV %s %s %s - %s", method, url, response, response.text)
            else:
                self.logger.debug("RECV %s %s %s", method, url, response)

            status_code = response.status_code

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                # Try parsing error message from the response
                msg: Optional[str] = None
                if response.text:
                    try:
                        msg = json.loads(response.text)["message"]
                    except (TypeError, KeyError, json.JSONDecodeError):
                        pass

                # HACK: sometimes Beaker doesn't use the right error code, so we try to guess based
                # on the message.
                if status_code == 400 and msg is not None and "already in use" in msg:
                    status_code = 409

                if exceptions_for_status is not None and status_code in exceptions_for_status:
                    raise exceptions_for_status[status_code]

                if msg is not None and status_code is not None and 400 <= status_code < 500:
                    # Raise a BeakerError if we're misusing the API (4xx error code).
                    if status_code == 403:
                        raise BeakerPermissionsError(msg)
                    else:
                        raise BeakerError(f"[code={status_code}] {msg}")
                elif msg is not None:
                    raise HTTPError(msg, response=response)  # type: ignore
                else:
                    raise

            return response

        if method in {"HEAD", "GET"}:
            # We assume HEAD and GET calls won't modify state, so they're
            # safe to retry for any recoverable error.
            make_request = retriable()(make_request)

        if self.beaker._session is not None:
            return make_request(self.beaker._session)
        else:
            with self.beaker._make_session() as session:
                return make_request(session)

    def rpc_connection(self):
        return self.beaker.rpc_connection()

    def rpc_request(
        self,
        method: grpc.UnaryUnaryMultiCallable,
        request: Message,
        response_type: Type[T],
        exceptions_for_status: Optional[Dict[grpc.StatusCode, Exception]] = None,
    ) -> T:
        del response_type
        try:
            return cast(T, method(request, metadata=self.beaker.rpc_call_metadata))
        except RpcError as e:
            if (
                exceptions_for_status is not None
                and isinstance(e, grpc.Call)
                and e.code() in exceptions_for_status
            ):
                raise exceptions_for_status[e.code()]
            else:
                raise

    def rpc_streaming_request(
        self,
        method: grpc.UnaryStreamMultiCallable,
        request: Message,
        response_type: Type[T],
        exceptions_for_status: Optional[Dict[grpc.StatusCode, Exception]] = None,
    ) -> Generator[T, None, None]:
        del response_type
        try:
            response = method(request, metadata=self.beaker.rpc_call_metadata)
            for item in response:
                yield cast(T, item)
        except RpcError as e:
            if (
                exceptions_for_status is not None
                and isinstance(e, grpc.Call)
                and e.code() in exceptions_for_status
            ):
                raise exceptions_for_status[e.code()]
            else:
                raise

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
            self.resolve_org(org)
            return cluster_name

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
            self.resolve_org(org)
            return workspace_name

    def resolve_cluster(self, cluster: Union[str, Cluster]) -> Cluster:
        if isinstance(cluster, Cluster):
            return cluster
        else:
            return self.beaker.cluster.get(cluster)

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

    def resolve_dataset(
        self, dataset: Union[str, Dataset], ensure_storage: bool = False
    ) -> Dataset:
        if isinstance(dataset, Dataset):
            if ensure_storage and dataset.storage is None:
                # Might need to get dataset again if 'storage' hasn't been set yet.
                dataset = self.beaker.dataset.get(dataset.id)
                if dataset.storage is None:
                    raise DatasetReadError(dataset.id)
            return dataset
        else:
            dataset = self.beaker.dataset.get(dataset)
            if ensure_storage and dataset.storage is None:
                raise DatasetReadError(dataset.id)
            return dataset

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

    def resolve_budget(self, budget: str) -> str:
        if "/" not in budget:
            return budget
        org_name, budget_name = budget.split("/", 1)
        with self.rpc_connection() as service:
            data = self.rpc_request(
                service.ResolveBudgetName,
                pb2.ResolveBudgetNameRequest(organization_name=org_name, budget_name=budget_name),
                pb2.ResolveBudgetNameResponse,
                exceptions_for_status={
                    grpc.StatusCode.NOT_FOUND: BudgetNotFound(budget),
                },
            )
        return data.budget_id

    def url_quote(self, id: str) -> str:
        return urllib.parse.quote(id, safe="")

    def validate_beaker_name(self, name: str):
        if not name.replace("-", "").replace("_", "").replace(".", "").isalnum():
            raise ValueError(
                f"Invalid name '{name}'. Beaker names can only contain letters, "
                f"digits, periods, dashes, and underscores."
            )
