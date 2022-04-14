from typing import Dict, List, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class WorkspaceClient(ServiceClient):
    """
    Accessed via :data:`Beaker.workspace <beaker.Beaker.workspace>`.
    """

    def get(self, workspace: Optional[str] = None) -> Workspace:
        """
        Get information about the workspace.

        :param workspace: The workspace name. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self._resolve_workspace_name(workspace)
        return Workspace.from_json(
            self.request(
                f"workspaces/{self._url_quote(workspace_name)}",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def create(self, workspace: str) -> Workspace:
        """
        Create a workspace.

        :param workspace: The workspace name.

        :raises ValueError: If the workspace name is invalid.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if workspace is None:
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = self._resolve_workspace_name(workspace)
        org, name = workspace_name.split("/", 1)
        return Workspace.from_json(
            self.request(
                "workspaces",
                method="POST",
                data={"name": name, "org": org},
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name)),
                    409: WorkspaceConflict(workspace_name),
                },
            ).json()
        )

    def ensure(self, workspace: str) -> Workspace:
        """
        Ensure that the given workspace exists.

        :param workspace: The workspace name.

        :raises ValueError: If the workspace name is invalid.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
            that doesn't exist.
        """
        try:
            return self.get(workspace)
        except WorkspaceNotFound:
            return self.create(workspace)

    def archive(self, workspace: Union[str, Workspace]) -> Workspace:
        """
        Archive a workspace, making it read-only.

        :param workspace: The workspace to archive.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceWriteError: If the workspace is already archived or you don't
            have the permissions to archive it.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if workspace is None:  # could accidentally archive default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = (
            workspace.full_name
            if isinstance(workspace, Workspace)
            else self._resolve_workspace_name(workspace)
        )
        return Workspace.from_json(
            self.request(
                f"workspaces/{self._url_quote(workspace_name)}",
                method="PATCH",
                data={"archive": True},
                exceptions_for_status={
                    403: WorkspaceWriteError(workspace_name),
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name)),
                },
            ).json()
        )

    def unarchive(self, workspace: Union[str, Workspace]) -> Workspace:
        """
        Unarchive a workspace.

        :param workspace: The workspace to unarchive.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if workspace is None:  # could accidentally unarchive default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = (
            workspace.full_name
            if isinstance(workspace, Workspace)
            else self._resolve_workspace_name(workspace)
        )
        return Workspace.from_json(
            self.request(
                f"workspaces/{self._url_quote(workspace_name)}",
                method="PATCH",
                data={"archive": False},
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def rename(self, workspace: Union[str, Workspace], new_name: str) -> Workspace:
        """
        Rename a workspace.

        :param workspace: The workspace to rename.
        :param new_name: The new name to assign to the workspace.
            This should only *not* include the organization.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceWriteError: If the workspace has been archived.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises ValueError: If the new name is invalid.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self._validate_workspace_name(new_name)
        if workspace is None:  # could accidentally rename default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = (
            workspace.full_name
            if isinstance(workspace, Workspace)
            else self._resolve_workspace_name(workspace)
        )
        return Workspace.from_json(
            self.request(
                f"workspaces/{self._url_quote(workspace_name)}",
                method="PATCH",
                data={"name": new_name},
                exceptions_for_status={
                    403: WorkspaceWriteError(workspace_name),
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name)),
                    409: WorkspaceConflict(new_name),
                },
            ).json()
        )

    def move(
        self,
        *items: Union[str, Image, Dataset, Experiment],
        workspace: Optional[Union[str, Workspace]] = None,
    ):
        """
        Move items into a workspace.

        :param items: The items to move into the workspace.
        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises WorkspaceWriteError: If the workspace has been archived.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self._resolve_workspace(workspace)
        self.request(
            f"workspaces/{self._url_quote(workspace.full_name)}/transfer",
            method="POST",
            data={"ids": [item if isinstance(item, str) else item.id for item in items]},
            exceptions_for_status={
                403: WorkspaceWriteError(workspace.full_name),
                404: WorkspaceNotFound(self._not_found_err_msg(workspace.full_name)),
            },
        )

    def list(
        self,
        org: Optional[Union[str, Organization]] = None,
        author: Optional[Union[str, Account]] = None,
        match: Optional[str] = None,
        archived: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Workspace]:
        """
        List workspaces belonging to an organization.

        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.
        :param author: Only list workspaces authored by this account.
        :param match: Only include workspaces matching the text.
        :param archived: Only include/exclude archived workspaces.
        :param limit: Limit the number of workspaces returned.

        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises AccountNotFound: If the author account doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self._resolve_org(org)
        workspaces: List[Workspace] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {"org": org.id}
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

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include images matching the text.
        :param limit: Limit the number of images returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self._resolve_workspace(workspace, read_only_ok=True)
        images: List[Image] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ImagesPage.from_json(
                self.request(
                    f"workspaces/{self._url_quote(workspace.full_name)}/images",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace.full_name))
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

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include experiments matching the text.
        :param limit: Limit the number of experiments returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self._resolve_workspace(workspace, read_only_ok=True)
        experiments: List[Experiment] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ExperimentsPage.from_json(
                self.request(
                    f"workspaces/{self._url_quote(workspace.full_name)}/experiments",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace.full_name))
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

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include datasets matching the text.
        :param results: Only include/exclude experiment result datasets.
        :param uncommitted: Only include/exclude uncommitted datasets.
        :param limit: Limit the number of datasets returned.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self._resolve_workspace(workspace, read_only_ok=True)
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
                    f"workspaces/{self._url_quote(workspace.full_name)}/datasets",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace.full_name))
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

    def secrets(self, workspace: Optional[Union[str, Workspace]] = None) -> List[Secret]:
        """
        List secrets in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises OrganizationNotSet: If the workspace name doesn't start with
            an organization and :data:`Config.default_org <beaker.Config.default_org>` is not set.
        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self._resolve_workspace(workspace, read_only_ok=True)
        return [
            Secret.from_json(d)
            for d in self.request(
                f"workspaces/{self._url_quote(workspace.full_name)}/secrets",
                method="GET",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace.full_name))
                },
            ).json()["data"]
        ]

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the workspace *full* name "
            f"(with the organization prefix, e.g. 'org/workspace_name')"
        )

    def _validate_workspace_name(self, name: str):
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"Workspace name can only contain letters, digits, dashes, and underscores: '{name}'"
            )
