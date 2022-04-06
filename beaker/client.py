from typing import Optional

import docker

from .config import Config
from .data_model import *
from .exceptions import *
from .services import *

__all__ = ["Beaker"]


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.

    :param config: The Beaker :class:`Config`.

    The easiest way to initialize a Beaker client is with :meth:`.from_env()`.
    """

    def __init__(self, config: Config):
        self._config = config
        self._docker: Optional[docker.DockerClient] = None

        # Initialize service clients:
        self._account = AccountClient(self)
        self._organization = OrganizationClient(self)
        self._workspace = WorkspaceClient(self)
        self._cluster = ClusterClient(self)
        self._dataset = DatasetClient(self)
        self._image = ImageClient(self)
        self._job = JobClient(self)
        self._experiment = ExperimentClient(self)

        # Ensure default workspace exists.
        if self._config.default_workspace is not None:
            self.workspace.ensure(self._config.default_workspace)

    @classmethod
    def from_env(cls, **overrides) -> "Beaker":
        """
        Initialize client from a config file and/or environment variables.

        :param overrides: Fields in the :class:`Config` to override.
        """
        return cls(Config.from_env(**overrides))

    @property
    def config(self) -> Config:
        """
        The client's :class:`Config`.
        """
        return self._config

    @property
    def account(self) -> AccountClient:
        """
        Manage accounts.
        """
        return self._account

    @property
    def organization(self) -> OrganizationClient:
        """
        Manage organizations.
        """
        return self._organization

    @property
    def workspace(self) -> WorkspaceClient:
        """
        Manage workspaces.
        """
        return self._workspace

    @property
    def cluster(self) -> ClusterClient:
        """
        Manage clusters.
        """
        return self._cluster

    @property
    def dataset(self) -> DatasetClient:
        """
        Manage datasets.
        """
        return self._dataset

    @property
    def image(self) -> ImageClient:
        """
        Manage images.
        """
        return self._image

    @property
    def job(self) -> JobClient:
        """
        Manage jobs.
        """
        return self._job

    @property
    def experiment(self) -> ExperimentClient:
        """
        Manage experiments.
        """
        return self._experiment

    @property
    def docker(self) -> docker.DockerClient:
        if self._docker is None:
            self._docker = docker.from_env()
        assert self._docker is not None
        return self._docker
