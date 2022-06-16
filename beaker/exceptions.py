"""
Exceptions that can be raised by the :class:`~beaker.Beaker` client.

.. tip::
    All exceptions inherit from :class:`BeakerError` other than :exc:`HTTPError`,
    which is re-exported from :exc:`requests.exceptions.HTTPError`,
    and :exc:`ValidationError`, which is re-exported from `pydantic <https://pydantic-docs.helpmanual.io/>`_.
"""

from pydantic import ValidationError  # noqa: F401, re-imported here for convenience
from requests.exceptions import (  # noqa: F401, re-imported here for convenience
    HTTPError,
)

ValidationError.__doc__ = """
Raised when data passed into a :mod:`DataModel <beaker.data_model>` is invalid.
"""


class BeakerError(Exception):
    """
    Base class for all Beaker errors other than :exc:`HTTPError`, which is re-exported
    from :exc:`requests.exceptions.HTTPError`, and :exc:`ValidationError`, which is
    re-exported from `pydantic <https://pydantic-docs.helpmanual.io/>`_.
    """


class AccountNotFound(BeakerError):
    pass


class OrganizationNotFound(BeakerError):
    """
    Raised when a specified organization doesn't exist.
    """


class OrganizationNotSet(BeakerError):
    """
    Raised when an identifying doesn't start with an organization name and
    :data:`Config.default_org <beaker.Config.default_org>` is not set.
    """


class ConfigurationError(BeakerError):
    """
    Raised when the :class:`~beaker.Config` fails to instantiate.
    """


class ImageNotFound(BeakerError):
    pass


class ImageConflict(BeakerError):
    """
    Raised when attempting to create/rename an image if an image by that name already exists.
    """


class WorkspaceNotFound(BeakerError):
    pass


class WorkspaceWriteError(BeakerError):
    """
    Raised when attempting to modify or add to a workspace that's been archived.
    """


class WorkspaceConflict(BeakerError):
    """
    Raised when attempting to create/rename a workspace if a workspace by that name already exists.
    """


class ClusterNotFound(BeakerError):
    pass


class ClusterConflict(BeakerError):
    """
    Raised when attempting to create a cluster if a cluster by that name already exists.
    """


class ExperimentNotFound(BeakerError):
    pass


class ExperimentConflict(BeakerError):
    """
    Raised when attempting to create/rename an experiment if an experiment by that name already exists.
    """


class DatasetConflict(BeakerError):
    """
    Raised when attempting to create/rename a dataset if a dataset by that name already exists.
    """


class DatasetNotFound(BeakerError):
    pass


class UnexpectedEOFError(BeakerError):
    """
    Raised when creating a dataset when an empty source file is encountered.
    """


class JobNotFound(BeakerError):
    pass


class WorkspaceNotSet(BeakerError):
    """
    Raised when workspace argument is not provided and there is no default workspace set.
    """


class NodeNotFound(BeakerError):
    pass


class DatasetWriteError(BeakerError):
    """
    Raised when a write operation on a dataset fails because the dataset has already been committed.
    """


class DatasetReadError(BeakerError):
    """
    Raised when a read operation on a dataset fails because the dataset hasn't been committed yet,
    or the :data:`~beaker.data_model.Dataset.storage` hasn't been set for some other reason.
    """


class SecretNotFound(BeakerError):
    pass


class GroupConflict(BeakerError):
    """
    Raised when attempting to create/rename a group if a group by that name already exists.
    """


class GroupNotFound(BeakerError):
    pass


class DuplicateJobError(BeakerError):
    """
    Raised when duplicate jobs are passed into a method that expects unique jobs.
    """


class DuplicateExperimentError(BeakerError):
    """
    Raised when duplicate experiments are passed into a method that expects unique experiments.
    """


class TaskNotFound(BeakerError):
    pass


class ChecksumFailedError(BeakerError):
    """
    Raised when a downloaded file from a Beaker dataset is corrupted.
    """


class JobFailedError(BeakerError):
    pass


class JobTimeoutError(BeakerError, TimeoutError):
    pass
