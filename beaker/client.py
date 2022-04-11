from typing import Optional

import docker
from cachetools import TTLCache, cached

from .config import Config
from .data_model import *
from .exceptions import *
from .services import *
from .version import VERSION

__all__ = ["Beaker"]


_UPGRADE_WARNING_ISSUED = False


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.

    :param config: The Beaker :class:`Config`.

    The easiest way to initialize a Beaker client is with :meth:`.from_env()`.
    """

    def __init__(self, config: Config, check_for_upgrades: bool = True):
        # See if there's a newer version, and if so, suggest that the user upgrades.
        if check_for_upgrades and not _UPGRADE_WARNING_ISSUED:
            self._check_for_upgrades()

        self._config = config
        self._docker: Optional[docker.DockerClient] = None

        # Initialize service clients:
        self._account = AccountClient(self)
        self._organization = OrganizationClient(self)
        self._workspace = WorkspaceClient(self)
        self._cluster = ClusterClient(self)
        self._node = NodeClient(self)
        self._dataset = DatasetClient(self)
        self._image = ImageClient(self)
        self._job = JobClient(self)
        self._experiment = ExperimentClient(self)
        self._secret = SecretClient(self)

        # Ensure default workspace exists.
        if self._config.default_workspace is not None:
            self.workspace.ensure(self._config.default_workspace)

    @staticmethod
    @cached(cache=TTLCache(maxsize=10, ttl=5 * 60))
    def _check_for_upgrades():
        import warnings

        import packaging.version
        import requests

        global _UPGRADE_WARNING_ISSUED

        try:
            response = requests.get(
                "https://api.github.com/repos/allenai/beaker-py/releases/latest", timeout=1
            )
            if response.ok:
                latest_version = packaging.version.parse(response.json()["tag_name"])
                if latest_version > packaging.version.parse(VERSION):
                    warnings.warn(
                        f"You're using beaker-py v{VERSION}, "
                        f"but a newer version (v{latest_version}) is available. "
                        f"Please upgrade with `pip install --upgrade beaker-py`.",
                        UserWarning,
                    )
                    _UPGRADE_WARNING_ISSUED = True
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass

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

        .. tip::
            See the `Accounts Overview <overview.html#accounts>`_ for a walk-through of the
            main methods, or check out the `Account API Docs <#account>`_
            to see all of the available methods.
        """
        return self._account

    @property
    def organization(self) -> OrganizationClient:
        """
        Manage organizations.

        .. tip::
            See the `Organizations Overview <overview.html#organizations>`_ for a walk-through of the
            main methods, or check out the `Organization API Docs <#organization>`_
            to see all of the available methods.
        """
        return self._organization

    @property
    def workspace(self) -> WorkspaceClient:
        """
        Manage workspaces.

        .. tip::
            See the `Workspaces Overview <overview.html#workspaces>`_ for a walk-through of the
            main methods, or check out the `Workspace API Docs <#workspace>`_
            to see all of the available methods.
        """
        return self._workspace

    @property
    def cluster(self) -> ClusterClient:
        """
        Manage clusters.

        .. tip::
            See the `Clusters Overview <overview.html#clusters>`_ for a walk-through of the
            main methods, or check out the `Cluster API Docs <#cluster>`_
            to see all of the available methods.
        """
        return self._cluster

    @property
    def node(self) -> NodeClient:
        """
        Manage nodes.

        .. tip::
            See the `Nodes Overview <overview.html#nodes>`_ for a walk-through of the
            main methods, or check out the `Node API Docs <#node>`_
            to see all of the available methods.
        """
        return self._node

    @property
    def dataset(self) -> DatasetClient:
        """
        Manage datasets.

        .. tip::
            See the `Datasets Overview <overview.html#datasets>`_ for a walk-through of the
            main methods, or check out the `Dataset API Docs <#dataset>`_
            to see all of the available methods.
        """
        return self._dataset

    @property
    def image(self) -> ImageClient:
        """
        Manage images.

        .. tip::
            See the `Images Overview <overview.html#images>`_ for a walk-through of the
            main methods, or check out the `Image API Docs <#image>`_
            to see all of the available methods.
        """
        return self._image

    @property
    def job(self) -> JobClient:
        """
        Manage jobs.

        .. tip::
            See the `Jobs Overview <overview.html#jobs>`_ for a walk-through of the
            main methods, or check out the `Job API Docs <#job>`_
            to see all of the available methods.
        """
        return self._job

    @property
    def experiment(self) -> ExperimentClient:
        """
        Manage experiments.

        .. tip::
            See the `Experiments Overview <overview.html#experiments>`_ for a walk-through of the
            main methods, or check out the `Experiment API Docs <#experiment>`_
            to see all of the available methods.
        """
        return self._experiment

    @property
    def secret(self) -> SecretClient:
        """
        Manage secrets.

        .. tip::
            See the `Secrets Overview <overview.html#secrets>`_ for a walk-through of the
            main methods, or check out the `Secret API Docs <#secret>`_
            to see all of the available methods.
        """
        return self._secret

    @property
    def docker(self) -> docker.DockerClient:
        if self._docker is None:
            self._docker = docker.from_env()
        assert self._docker is not None
        return self._docker
