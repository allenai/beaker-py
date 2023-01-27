from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Type, TypeVar, Union

from ..data_model import *
from ..exceptions import *
from ..util import format_cursor
from .service_client import ServiceClient

T = TypeVar("T")


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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        self, workspace: str, *, description: Optional[str] = None, public: bool = False
    ) -> Workspace:
        """
        Create a workspace.

        :param workspace: The workspace name.
        :param description: Text description for the workspace.
        :param public: If the workspace should be public.

        :raises ValueError: If the workspace name is invalid.
        :raises WorkspaceConflict: If a workspace by that name already exists.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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

    def _paginated_requests(
        self,
        page_class: Type[BasePage[T]],
        path: str,
        query: Dict[str, Any],
        limit: Optional[int] = None,
        workspace_name: Optional[str] = None,
    ) -> Generator[T, None, None]:
        if limit:
            query["limit"] = str(limit)

        exceptions_for_status: Optional[Dict[int, Exception]] = (
            None
            if workspace_name is None
            else {404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))}
        )

        count = 0
        while True:
            page = page_class.from_json(
                self.request(
                    path,
                    method="GET",
                    query=query,
                    exceptions_for_status=exceptions_for_status,
                ).json()
            )
            for x in page.data:
                count += 1
                yield x
                if limit is not None and count >= limit:
                    return

            query["cursor"] = page.next_cursor or page.next
            if not query["cursor"]:
                break

    def iter(
        self,
        org: Optional[Union[str, Organization]] = None,
        *,
        author: Optional[Union[str, Account]] = None,
        match: Optional[str] = None,
        archived: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: WorkspaceSort = WorkspaceSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> Generator[Workspace, None, None]:
        org = self.resolve_org(org)
        query: Dict[str, str] = {
            "org": org.id,
            "field": str(sort_by),
            "order": "descending" if descending else "ascending",
            "cursor": format_cursor(cursor),
        }
        if author is not None:
            query["author"] = (
                author.name if isinstance(author, Account) else self.beaker.account.get(author).name
            )
        if match is not None:
            query["q"] = match
        if archived is not None:
            query["archived"] = str(archived).lower()

        yield from self._paginated_requests(WorkspacePage, "workspaces", query, limit=limit)

    def list(
        self,
        org: Optional[Union[str, Organization]] = None,
        *,
        author: Optional[Union[str, Account]] = None,
        match: Optional[str] = None,
        archived: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: WorkspaceSort = WorkspaceSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> List[Workspace]:
        """
        List workspaces belonging to an organization.

        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.
        :param author: Only list workspaces authored by this account.
        :param match: Only include workspaces matching the text.
        :param archived: Only include/exclude archived workspaces.
        :param limit: Limit the number of workspaces returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises AccountNotFound: If the author account doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return list(
            self.iter(
                org=org,
                author=author,
                match=match,
                archived=archived,
                limit=limit,
                sort_by=sort_by,
                descending=descending,
                cursor=cursor,
            )
        )

    def iter_images(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: ImageSort = ImageSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> Generator[Image, None, None]:
        """
        Iterate over the images in a workspace.

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include images matching the text.
        :param limit: Limit the number of images returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        query: Dict[str, str] = {
            "field": str(sort_by),
            "order": "descending" if descending else "ascending",
            "cursor": format_cursor(cursor),
        }
        if match is not None:
            query["q"] = match

        yield from self._paginated_requests(
            ImagesPage,
            f"workspaces/{self.url_quote(workspace_name)}/images",
            query,
            limit=limit,
            workspace_name=workspace_name,
        )

    def images(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: ImageSort = ImageSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> List[Image]:
        """
        List the images in a workspace.

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include images matching the text.
        :param limit: Limit the number of images returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return list(
            self.iter_images(
                workspace=workspace,
                match=match,
                limit=limit,
                sort_by=sort_by,
                descending=descending,
                cursor=cursor,
            )
        )

    def iter_experiments(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: ExperimentSort = ExperimentSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> Generator[Experiment, None, None]:
        """
        Iterate over the experiments in a workspace.

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include experiments matching the text.
        :param limit: Limit the number of experiments returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        query: Dict[str, str] = {
            "field": str(sort_by),
            "order": "descending" if descending else "ascending",
            "cursor": format_cursor(cursor),
        }
        if match is not None:
            query["q"] = match

        yield from self._paginated_requests(
            ExperimentsPage,
            f"workspaces/{self.url_quote(workspace_name)}/experiments",
            query,
            limit=limit,
            workspace_name=workspace_name,
        )

    def experiments(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: ExperimentSort = ExperimentSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> List[Experiment]:
        """
        List the experiments in a workspace.

        :param workspace: The Beaker workspace name or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include experiments matching the text.
        :param limit: Limit the number of experiments returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return list(
            self.iter_experiments(
                workspace=workspace,
                match=match,
                limit=limit,
                sort_by=sort_by,
                descending=descending,
                cursor=cursor,
            )
        )

    def iter_datasets(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        results: Optional[bool] = None,
        uncommitted: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: DatasetSort = DatasetSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> Generator[Dataset, None, None]:
        """
        Iterate over the datasets in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include datasets matching the text.
        :param results: Only include/exclude experiment result datasets.
        :param uncommitted: Only include/exclude uncommitted datasets.
        :param limit: Limit the number of datasets returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        query: Dict[str, str] = {
            "field": str(sort_by),
            "order": "descending" if descending else "ascending",
            "cursor": format_cursor(cursor),
        }
        if match is not None:
            query["q"] = match
        if results is not None:
            query["results"] = str(results).lower()
        if uncommitted is not None:
            query["committed"] = str(not uncommitted).lower()

        yield from self._paginated_requests(
            DatasetsPage,
            f"workspaces/{self.url_quote(workspace_name)}/datasets",
            query,
            limit=limit,
            workspace_name=workspace_name,
        )

    def datasets(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        results: Optional[bool] = None,
        uncommitted: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: DatasetSort = DatasetSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> List[Dataset]:
        """
        List the datasets in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include datasets matching the text.
        :param results: Only include/exclude experiment result datasets.
        :param uncommitted: Only include/exclude uncommitted datasets.
        :param limit: Limit the number of datasets returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return list(
            self.iter_datasets(
                workspace=workspace,
                match=match,
                results=results,
                uncommitted=uncommitted,
                limit=limit,
                sort_by=sort_by,
                descending=descending,
                cursor=cursor,
            )
        )

    def secrets(self, workspace: Optional[Union[str, Workspace]] = None) -> List[Secret]:
        """
        List secrets in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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

    def iter_groups(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: GroupSort = GroupSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> Generator[Group, None, None]:
        """
        Iterate over groups in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include groups matching the text.
        :param limit: Limit the number of groups returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        workspace_name = self.resolve_workspace(workspace, read_only_ok=True).full_name
        query: Dict[str, str] = {
            "field": str(sort_by),
            "order": "descending" if descending else "ascending",
            "cursor": format_cursor(cursor),
        }
        if match is not None:
            query["q"] = match

        yield from self._paginated_requests(
            GroupsPage,
            f"workspaces/{self.url_quote(workspace_name)}/groups",
            query,
            limit=limit,
            workspace_name=workspace_name,
        )

    def groups(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        match: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: GroupSort = GroupSort.created,
        descending: bool = True,
        cursor: int = 0,
    ) -> List[Group]:
        """
        List groups in a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param match: Only include groups matching the text.
        :param limit: Limit the number of groups returned.
        :param sort_by: The field to sort the results by.
        :param descending: Order the results in descending order according to the ``sort_by`` field.
        :param cursor: Set the starting cursor for the query. You can use this to paginate the results.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return list(
            self.iter_groups(
                workspace=workspace,
                match=match,
                limit=limit,
                sort_by=sort_by,
                descending=descending,
                cursor=cursor,
            )
        )

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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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

    def clear(
        self,
        workspace: Optional[Union[str, Workspace]] = None,
        *,
        groups: bool = True,
        experiments: bool = True,
        images: bool = True,
        datasets: bool = True,
        secrets: bool = True,
        older_than: Optional[datetime] = None,
    ):
        """
        Remove groups, experiments, images, datasets, and secrets from a workspace.

        :param workspace: The Beaker workspace name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param groups: Whether to delete groups.
        :param experiments: Whether to delete experiments.
        :param images: Whether to delete images.
        :param datasets: Whether to delete datasets.
        :param secrets: Whether to delete secrets.
        :param older_than: Only delete objects created before this date.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        import concurrent.futures
        from itertools import chain

        def should_delete(created: Optional[datetime]) -> bool:
            if older_than is None or created is None:
                return True
            if any([dt.tzinfo is None for dt in (created, older_than)]):
                return created.replace(tzinfo=None) < older_than.replace(tzinfo=None)
            else:
                return created < older_than

        deletion_counts: Dict[str, int] = defaultdict(int)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            deletion_futures = []

            if groups:
                for group in filter(lambda x: should_delete(x.created), self.groups(workspace)):
                    future = executor.submit(self.beaker.group.delete, group)
                    deletion_futures.append(future)
                    deletion_counts["groups_deleted"] += 1

            if experiments:
                for experiment in filter(
                    lambda x: should_delete(x.created), self.iter_experiments(workspace)
                ):
                    future = executor.submit(self.beaker.experiment.delete, experiment)
                    deletion_futures.append(future)
                    deletion_counts["experiments_deleted"] += 1

            if images:
                for image in filter(
                    lambda x: should_delete(x.committed), self.iter_images(workspace)
                ):
                    future = executor.submit(self.beaker.image.delete, image)
                    deletion_futures.append(future)
                    deletion_counts["images_deleted"] += 1

            if datasets:
                for dataset in filter(
                    lambda x: should_delete(x.created),
                    chain(
                        self.iter_datasets(workspace),
                        self.iter_datasets(workspace, uncommitted=True),
                    ),
                ):
                    future = executor.submit(self.beaker.dataset.delete, dataset)
                    deletion_futures.append(future)
                    deletion_counts["datasets_deleted"] += 1

            if secrets:
                for secret in filter(lambda x: should_delete(x.created), self.secrets(workspace)):
                    future = executor.submit(self.beaker.secret.delete, secret, workspace)
                    deletion_futures.append(future)
                    deletion_counts["secrets_deleted"] += 1

            done, _ = concurrent.futures.wait(deletion_futures)
            for future in done:
                try:
                    future.result()
                except NotFoundError:
                    pass

        return WorkspaceClearResult(**deletion_counts)

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the workspace ID or *full* name "
            f"(with the organization prefix, e.g. 'org/workspace_name')."
        )
