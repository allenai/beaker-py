from contextlib import contextmanager
from typing import Generator, Optional, Tuple, Union

import docker
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import Config
from .data_model import *
from .exceptions import *
from .services import *

__all__ = ["Beaker"]


_LATEST_VERSION_CHECKED = False


class Beaker:
    """
    A client for interacting with `Beaker <https://beaker.org>`_.

    :param config: The Beaker :class:`Config`.
    :param check_for_upgrades: Automatically check that beaker-py is up-to-date. You'll see
        a warning if it isn't.
    :param timeout: How many seconds to wait for the Beaker server to send data before giving up,
        as a float, or a (connect timeout, read timeout) tuple.
    :param session: Set to ``True`` or a :class:`requests.Session` instance to
        force the Beaker client to use a single :class:`~requests.Session`
        for all HTTP requests to the Beaker server for the life of the client.

        .. seealso::
            The :meth:`session()` context manager.

        .. warning::
            You should only set this argument for short-lived clients.
            If you're initializing a :class:`Beaker` client with this that's supposed to stick
            around indefinitely, consider using the :meth:`session()` context manager
            intermittently instead.

    The easiest way to initialize a Beaker client is with :meth:`.from_env()`:

    >>> beaker = Beaker.from_env()

    You can then interact with the various Beaker services through the corresponding
    property. For example, to manage workspaces, use :data:`Beaker.workspace`:

    >>> beaker.workspace.get(workspace_name).full_name
    'ai2/beaker-py-testing'

    .. tip::
        Use the right side nav to browse through the API docs for all of the different services.

    """

    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(
        self,
        config: Config,
        check_for_upgrades: bool = True,
        timeout: Optional[Union[float, Tuple[float, float]]] = 5.0,
        session: Optional[Union[bool, requests.Session]] = None,
    ):
        # See if there's a newer version, and if so, suggest that the user upgrades.
        if check_for_upgrades:
            self._check_for_upgrades()

        self._config = config
        self._docker: Optional[docker.DockerClient] = None
        self._session: Optional[requests.Session] = (
            None
            if not session
            else (session if isinstance(session, requests.Session) else self._make_session())
        )
        self._timeout = timeout

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
        self._group = GroupClient(self)

        # Ensure default workspace exists.
        if self._config.default_workspace is not None:
            if self._config.default_workspace == "":
                raise ValueError("'default_workspace' cannot be an empty string")
            self.workspace.ensure(self._config.default_workspace)

        # Validate default org.
        if self._config.default_org is not None:
            if self._config.default_org == "":
                raise ValueError("'default_org' cannot be an empty string")
            self.organization.get(self._config.default_org)

    def __str__(self) -> str:
        return (
            f"Beaker("
            f"user='{self.account.name}', "
            f"default_workspace='{self.config.default_workspace}', "
            f"default_org='{self.config.default_org}', "
            f"agent_address='{self.config.agent_address}'"
            f")"
        )

    @staticmethod
    def _check_for_upgrades():
        global _LATEST_VERSION_CHECKED

        if _LATEST_VERSION_CHECKED:
            return

        import warnings

        import packaging.version
        import requests

        from .version import VERSION

        try:
            response = requests.get(
                "https://api.github.com/repos/allenai/beaker-py/releases/latest", timeout=1
            )
            if response.ok:
                latest_version = packaging.version.parse(response.json()["tag_name"])
                _LATEST_VERSION_CHECKED = True
                if latest_version > packaging.version.parse(VERSION):
                    warnings.warn(
                        f"You're using beaker-py v{VERSION}, "
                        f"but a newer version (v{latest_version}) is available.\n\n"
                        f"Please upgrade with `pip install --upgrade beaker-py`.\n\n"
                        f"You can find the release notes for v{latest_version} at "
                        f"https://github.com/allenai/beaker-py/releases/tag/v{latest_version}\n",
                        UserWarning,
                    )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass

    @classmethod
    def from_env(
        cls,
        check_for_upgrades: bool = True,
        timeout: Optional[Union[float, Tuple[float, float]]] = 5.0,
        session: Optional[Union[bool, requests.Session]] = None,
        **overrides,
    ) -> "Beaker":
        """
        Initialize client from a config file and/or environment variables.

        :param check_for_upgrades: Automatically check that beaker-py is up-to-date. You'll see
            a warning if it isn't.

        :param timeout: How many seconds to wait for the Beaker server to send data before giving up,
            as a float, or a (connect timeout, read timeout) tuple.

        :param session: Set to ``True`` or a :class:`requests.Session` instance to
            force the Beaker client to use a single :class:`~requests.Session`
            for all HTTP requests to the Beaker server.

            .. seealso::
                The :meth:`session()` context manager.

            .. warning::
                You should only set this argument for short-lived clients.
                If you're initializing a :class:`Beaker` client with this that's supposed to stick
                around indefinitely, consider using the :meth:`session()` context manager
                intermittently instead.

        :param overrides: Fields in the :class:`Config` to override.

        .. note::
            This will use the same config file that the `Beaker command-line client
            <https://github.com/allenai/beaker/>`_
            creates and uses, which is usually located at ``$HOME/.beaker/config.yml``.

            If you haven't configured the command-line client, then you can alternately just
            set the environment variable ``BEAKER_TOKEN`` to your Beaker `user token <https://beaker.org/user>`_.
        """
        return cls(
            Config.from_env(**overrides),
            check_for_upgrades=check_for_upgrades,
            timeout=timeout,
            session=session,
        )

    def _make_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=self.RECOVERABLE_SERVER_ERROR_CODES,
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    @contextmanager
    def session(self, session: Optional[requests.Session] = None) -> Generator[None, None, None]:
        """
        A context manager that forces the Beaker client to reuse a single :class:`requests.Session`
        for all HTTP requests to the Beaker server.

        This can improve performance when calling a series of a client methods in a row.

        :param session: The session to use.
            If not provided a default will be used.

            .. warning::
                Only set the ``session`` argument if you really know what you're doing! Otherwise
                just leave this as ``None``.

        :examples:

        >>> with beaker.session():
        ...     n_images = len(beaker.workspace.images())
        ...     n_datasets = len(beaker.workspace.datasets())

        """
        current = self._session
        session: requests.Session = session or self._make_session()
        try:
            self._session = session
            yield None
        finally:
            self._session = current
            session.close()

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

        :examples:

        >>> beaker.account.name
        'petew'

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

        :examples:

        >>> beaker.organization.get("ai2").display_name
        'AI2'

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

        :examples:

        >>> beaker.workspace.datasets(
        ...     match="squad",
        ...     uncommitted=False,
        ...     results=False,
        ... )[0].full_name
        'petew/squad-train'

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

        :examples:

        >>> beaker.cluster.get(beaker_cloud_cluster_name).autoscale
        True

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

        :examples:

        >>> beaker.node.get(beaker_node_id).limits.gpu_count
        8

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

        :examples:

        >>> [file_info.path for file_info in beaker.dataset.ls("petew/squad-train")]
        ['squad-train.arrow']

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

        :examples:

        >>> beaker.image.get("petew/hello-world").original_tag
        'hello-world'

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

        :examples:

        >>> running_jobs = beaker.job.list(
        ...     beaker_on_prem_cluster_name,
        ...     finalized=False,
        ... )

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

        :examples:

        >>> logs = "".join([
        ...     line.decode() for line in
        ...     beaker.experiment.logs("petew/hello-world", quiet=True)
        ... ])
        <BLANKLINE>

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

        :examples:

        >>> secret = beaker.secret.write(secret_name, "foo")

        .. tip::
            See the `Secrets Overview <overview.html#secrets>`_ for a walk-through of the
            main methods, or check out the `Secret API Docs <#secret>`_
            to see all of the available methods.
        """
        return self._secret

    @property
    def group(self) -> GroupClient:
        """
        Manage groups.

        :examples:

        >>> group = beaker.group.create(group_name)

        .. tip::
            See the `Groups Overview <overview.html#groups>`_ for a walk-through of the
            main methods, or check out the `Group API Docs <#group>`_
            to see all of the available methods.
        """
        return self._group

    @property
    def docker(self) -> docker.DockerClient:
        if self._docker is None:
            self._docker = docker.from_env()
        assert self._docker is not None
        return self._docker
