from typing import Optional

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

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the *full* name of the workspace "
            f"(with the organization prefix, e.g. 'org/workspace_name')"
        )
