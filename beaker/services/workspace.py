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

        :param workspace: The workspace name or ID. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace = workspace or self.config.default_workspace
        if workspace is None:
            raise WorkspaceNotSet("'workspace' argument required since default workspace not set")

        def _get(id: str) -> Workspace:
            return Workspace.from_json(
                self.request(
                    f"workspaces/{self.url_quote(id)}",
                    exceptions_for_status={404: WorkspaceNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be a workspace ID, so we try that first before trying to resolve the name.
            return _get(workspace)
        except WorkspaceNotFound:
            try:
                # That didn't work, so now we'll try to resolve the name.
                workspace_name = self.resolve_workspace_name(workspace)
                return _get(workspace_name)
            except (ValueError, OrganizationNotSet, WorkspaceNotFound):
                # If the name was invalid, we'll just raise the original error.
                pass
            raise

    def create(
        self, workspace: str, description: Optional[str] = None, public: bool = False
    ) -> Workspace:
        """
        Create a workspace.

        :param workspace: The workspace name.
        :param description: Text description for the workspace.
        :param public: If the workspace should be public.

        :raises ValueError: If the workspace name is invalid.
        :raises WorkspaceConflict: If a workspace by that name already exists.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace_name(workspace)
        org, name = workspace_name.split("/", 1)
        return Workspace.from_json(
            self.request(
                "workspaces",
                method="POST",
                data=WorkspaceSpec(name=name, org=org, description=description, public=public),
                exceptions_for_status={
                    409: WorkspaceConflict(workspace_name),
                },
            ).json()
        )

    def ensure(self, workspace: str) -> Workspace:
        """
        Ensure that the given workspace exists.

        :param workspace: The workspace name.

        :raises ValueError: If the workspace name is invalid.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if workspace is None:  # could accidentally archive default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = self.resolve_workspace(workspace).full_name
        return Workspace.from_json(
            self.request(
                f"workspaces/{self.url_quote(workspace_name)}",
                method="PATCH",
                data=WorkspacePatch(archive=True),
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if workspace is None:  # could accidentally unarchive default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        return Workspace.from_json(
            self.request(
                f"workspaces/{self.url_quote(workspace_name)}",
                method="PATCH",
                data=WorkspacePatch(archive=False),
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def rename(self, workspace: Union[str, Workspace], name: str) -> Workspace:
        """
        Rename a workspace.

        :param workspace: The workspace to rename.
        :param name: The new name to assign to the workspace.
            This should only *not* include the organization.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises ValueError: If the new name is invalid.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        if workspace is None:  # could accidentally rename default workspace if None
            raise TypeError("Expected 'str', got 'NoneType'")
        workspace_name = self.resolve_workspace(workspace).full_name
        return Workspace.from_json(
            self.request(
                f"workspaces/{self.url_quote(workspace_name)}",
                method="PATCH",
                data=WorkspacePatch(name=name),
                exceptions_for_status={
                    403: WorkspaceWriteError(workspace_name),
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name)),
                    409: WorkspaceConflict(name),
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
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace).full_name
        self.request(
            f"workspaces/{self.url_quote(workspace_name)}/transfer",
            method="POST",
            data=WorkspaceTransferSpec(
                ids=[item if isinstance(item, str) else item.id for item in items]
            ),
            exceptions_for_status={
                403: WorkspaceWriteError(workspace_name),
                404: WorkspaceNotFound(self._not_found_err_msg(workspace_name)),
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

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises AccountNotFound: If the author account doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
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
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        images: List[Image] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ImagesPage.from_json(
                self.request(
                    f"workspaces/{self.url_quote(workspace_name)}/images",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
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
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        experiments: List[Experiment] = []
        cursor: Optional[str] = None
        query: Dict[str, str] = {}
        if match is not None:
            query["q"] = match

        while True:
            query["cursor"] = cursor or ""
            page = ExperimentsPage.from_json(
                self.request(
                    f"workspaces/{self.url_quote(workspace_name)}/experiments",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
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
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
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
                    f"workspaces/{self.url_quote(workspace_name)}/datasets",
                    method="GET",
                    query=query,
                    exceptions_for_status={
                        404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
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
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        return [
            Secret.from_json(d)
            for d in self.request(
                f"workspaces/{self.url_quote(workspace_name)}/secrets",
                method="GET",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()["data"]
        ]

    def groups(self, workspace: Optional[Union[str, Workspace]] = None) -> List[Group]:
        """
        List groups in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        return [
            Group.from_json(d)
            for d in self.request(
                f"workspaces/{self.url_quote(workspace_name)}/groups",
                method="GET",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()["data"]
        ]

    def get_permissions(
        self, workspace: Optional[Union[str, Workspace]] = None
    ) -> WorkspacePermissions:
        """
        Get workspace permissions.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        return WorkspacePermissions.from_json(
            self.request(
                f"workspaces/{self.url_quote(workspace_name)}/auth",
                method="GET",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def grant_permissions(
        self,
        auth: Permission,
        *accounts: Union[str, Account],
        workspace: Optional[Union[str, Workspace]] = None,
    ) -> WorkspacePermissions:
        """
        Grant workspace permissions to accounts.

        :param auth: The authorization level to grant (e.g. "read", "write", "all").
        :param accounts: The accounts to grant permissions to.
        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises ValueError: If ``auth`` is invalid.
        :raises AccountNotFound: If an account doesn't exist.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        if auth not in set(Permission):
            raise ValueError(f"Authorization '{auth}' is invalid")
        account_ids = [
            account.id if isinstance(account, Account) else self.beaker.account.get(account).id
            for account in accounts
        ]
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        self.request(
            f"workspaces/{self.url_quote(workspace_name)}/auth",
            method="PATCH",
            data=WorkspacePermissionsPatch(
                authorizations={account_id: auth for account_id in account_ids}
            ),
        )
        return self.get_permissions(workspace=workspace_name)

    def set_visibility(
        self, public: bool = False, workspace: Optional[Union[str, Workspace]] = None
    ) -> WorkspacePermissions:
        """
        Set workspace visibility to public or private.

        :param public: Public visibility.
        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        self.request(
            f"workspaces/{self.url_quote(workspace_name)}/auth",
            method="PATCH",
            data=WorkspacePermissionsPatch(public=public),
            exceptions_for_status={404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))},
        )
        return self.get_permissions(workspace=workspace_name)

    def revoke_permissions(
        self, *accounts: Union[str, Account], workspace: Optional[Union[str, Workspace]] = None
    ) -> WorkspacePermissions:
        """
        Revoke workspace permissions to accounts.

        :param accounts: The accounts to revoke permissions for.
        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises AccountNotFound: If an account doesn't exist.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        account_ids = [
            account.id if isinstance(account, Account) else self.beaker.account.get(account).id
            for account in accounts
        ]
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        self.request(
            f"workspaces/{self.url_quote(workspace_name)}/auth",
            method="PATCH",
            data=WorkspacePermissionsPatch(
                authorizations={account_id: Permission.no_permission for account_id in account_ids}
            ),
            exceptions_for_status={404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))},
        )
        return self.get_permissions(workspace=workspace_name)

    def url(self, workspace: Optional[Union[str, Workspace]] = None) -> str:
        """
        Get the URL for a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        return f"{self.config.agent_address}/ws/{workspace_name}"

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the workspace ID or *full* name "
            f"(with the organization prefix, e.g. 'org/workspace_name')."
        )
