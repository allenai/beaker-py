from typing import Dict, List, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class WorkspaceClient(ServiceClient):
    def get(self, workspace: Optional[str] = None) -> Workspace:
        """
        Get information about the workspace.

        :param workspace: The workspace name. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return Workspace.from_json(
            self.request(
                f"workspaces/{self._url_quote(workspace_name)}",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def ensure(self, workspace: str):
        """
        Ensure that the given workspace exists.

        :param workspace: The full workspace name.

        :raises HTTPError: Any other HTTP exception that can occur.
        :raises ValueError: If the workspace name is invalid.

        """
        try:
            self.get(workspace)
        except WorkspaceNotFound:
            try:
                org, name = workspace.split("/")
            except ValueError:
                raise ValueError(f"Invalided workspace name '{workspace}'")
            self.request("workspaces", method="POST", data={"name": name, "org": org})

    def list(
        self,
        org: Union[str, Organization],
        author: Optional[Union[str, Account]] = None,
        match: Optional[str] = None,
        archived: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Workspace]:
        """
        List workspaces belonging to an organization.

        :param org: The organization name or object.
        :param author: Only list workspaces authored by this account.
        :param match: Only include workspaces matching the text.
        :param archived: Only include/exclude archived workspaces.
        :param limit: Limit the number of workspaces returned.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises AccountNotFound: If the author account doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        organization_id = (
            org.id if isinstance(org, Organization) else self.beaker.organization.get(org).id
        )
        workspaces: List[Workspace] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {"org": organization_id}
        if author is not None:
            query["author"] = (
                author.name if isinstance(author, Account) else self.beaker.account.get(author).name
            )
        if match is not None:
            query["q"] = match
        if archived is not None:
            query["archived"] = str(archived).lower()
        if limit:
            query["limit"] = str(limit)

        while True:
            query["cursor"] = cursor or ""
            page = WorkspacePage.from_json(
                self.request(
                    "workspaces",
                    method="GET",
                    query=query,
                ).json()
            )
            workspaces.extend(page.data)
            cursor = page.next_cursor
            if not cursor:
                break
            if limit and len(workspaces) >= limit:
                workspaces = workspaces[:limit]
                break

        return workspaces

    def images(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        match: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Image]:
        """
        List the images in a workspace.

        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include images matching the text.
        :param limit: Limit the number of images returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_id = (
            workspace.id if isinstance(workspace, Workspace) else self._resolve_workspace(workspace)
        )
        images: List[Image] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ImagesPage.from_json(
                self.request(
                    f"workspaces/{self._url_quote(workspace_id)}/images",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_id))
                    },
                ).json()
            )
            images.extend(page.data)
            cursor = page.next_cursor
            if not cursor:
                break
            if limit is not None and len(images) >= limit:
                images = images[:limit]
                break

        return images

    def experiments(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        match: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Experiment]:
        """
        List the experiments in a workspace.

        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include experiments matching the text.
        :param limit: Limit the number of experiments returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_id = (
            workspace.id if isinstance(workspace, Workspace) else self._resolve_workspace(workspace)
        )
        experiments: List[Experiment] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ExperimentsPage.from_json(
                self.request(
                    f"workspaces/{self._url_quote(workspace_id)}/experiments",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_id))
                    },
                ).json()
            )
            experiments.extend(page.data)
            cursor = page.next_cursor
            if not cursor:
                break
            if limit is not None and len(experiments) >= limit:
                experiments = experiments[:limit]
                break

        return experiments

    def datasets(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        match: Optional[str] = None,
        results: Optional[bool] = None,
        uncommitted: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Dataset]:
        """
        List the datasets in a workspace.

        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include datasets matching the text.
        :param results: Only include/exclude experiment result datasets.
        :param uncommitted: Only include/exclude uncommitted datasets.
        :param limit: Limit the number of datasets returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_id = (
            workspace.id if isinstance(workspace, Workspace) else self._resolve_workspace(workspace)
        )
        datasets: List[Dataset] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match
        if results is not None:
            query["results"] = str(results).lower()
        if uncommitted is not None:
            query["committed"] = str(not uncommitted).lower()

        while True:
            query["cursor"] = cursor or ""
            page = DatasetsPage.from_json(
                self.request(
                    f"workspaces/{self._url_quote(workspace_id)}/datasets",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_id))
                    },
                ).json()
            )
            datasets.extend(page.data)
            cursor = page.next_cursor
            if not cursor:
                break
            if limit is not None and len(datasets) >= limit:
                datasets = datasets[:limit]
                break

        return datasets

    def secrets(self, workspace: Union[str, Workspace] = None) -> List[Secret]:
        """
        List secrets in a workspace.

        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_id = (
            workspace.id if isinstance(workspace, Workspace) else self._resolve_workspace(workspace)
        )
        return [
            Secret.from_json(d)
            for d in self.request(
                f"workspaces/{self._url_quote(workspace_id)}/secrets",
                method="GET",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_id))
                },
            ).json()["data"]
        ]

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the *full* name of the workspace "
            f"(with the organization prefix, e.g. 'org/workspace_name')"
        )
