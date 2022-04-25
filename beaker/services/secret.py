from typing import Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class SecretClient(ServiceClient):
    """
    Accessed via :data:`Beaker.secret <beaker.Beaker.secret>`.
    """

    def get(self, secret: str, workspace: Optional[Union[str, Workspace]] = None) -> Secret:
        """
        Get metadata about a secret.

        :param secret: The name of the secret.
        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises SecretNotFound: If the secret doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self.resolve_workspace(workspace, read_only_ok=True)
        return Secret.from_json(
            self.request(
                f"workspaces/{workspace.id}/secrets/{self.url_quote(secret)}",
                method="GET",
                exceptions_for_status={404: SecretNotFound(secret)},
            ).json()
        )

    def read(
        self, secret: Union[str, Secret], workspace: Optional[Union[str, Workspace]] = None
    ) -> str:
        """
        Read the value of a secret.

        :param secret: The secret name or object.
        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises SecretNotFound: If the secret doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self.resolve_workspace(workspace, read_only_ok=True)
        name = secret.name if isinstance(secret, Secret) else secret
        return self.request(
            f"workspaces/{workspace.id}/secrets/{self.url_quote(name)}/value",
            method="GET",
        ).content.decode()

    def write(
        self, name: str, value: str, workspace: Optional[Union[str, Workspace]] = None
    ) -> Secret:
        """
        Write a new secret or update an existing one.

        :param name: The name of the secret.
        :param value: The value to write to the secret.
        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self.resolve_workspace(workspace)
        return Secret.from_json(
            self.request(
                f"workspaces/{workspace.id}/secrets/{self.url_quote(name)}/value",
                method="PUT",
                data=value.encode(),
            ).json()
        )

    def delete(self, secret: Union[str, Secret], workspace: Optional[Union[str, Workspace]] = None):
        """
        Permanently delete a secret.

        :param secret: The secret name or object.
        :param workspace: The Beaker workspace ID, full name, or object. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises SecretNotFound: If the secret doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace: Workspace = self.resolve_workspace(workspace)
        name = secret.name if isinstance(secret, Secret) else secret
        return self.request(
            f"workspaces/{workspace.id}/secrets/{self.url_quote(name)}",
            method="DELETE",
            exceptions_for_status={404: SecretNotFound(secret)},
        )
