"""
Exceptions that can be raised by the :class:`~beaker.Beaker` client.

.. tip::
    All exceptions inherit from :class:`BeakerError` other than :exc:`HTTPError`,
    which is re-exported from :exc:`requests.exceptions.HTTPError`,
    and :exc:`ValidationError`, which is re-exported from `pydantic <https://pydantic-docs.helpmanual.io/>`_.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import ValidationError  # noqa: F401, re-imported here for convenience
from requests.exceptions import (  # noqa: F401, re-imported here for convenience
    HTTPError,
    RequestException,
)

if TYPE_CHECKING:
    from .data_model.experiment import Task
    from .data_model.job import Job

ValidationError.__doc__ = """
Raised when data passed into a :mod:`DataModel <beaker.data_model>` is invalid.
"""


__all__ = [
    "BeakerError",
    "ValidationError",
    "HTTPError",
    "RequestException",
    "NotFoundError",
    "AccountNotFound",
    "OrganizationNotFound",
    "OrganizationNotSet",
    "ConfigurationError",
    "ImageNotFound",
    "ImageConflict",
    "WorkspaceNotFound",
    "WorkspaceWriteError",
    "WorkspaceConflict",
    "ClusterNotFound",
    "ClusterConflict",
    "ExperimentNotFound",
    "ExperimentConflict",
    "DatasetConflict",
    "DatasetNotFound",
    "UnexpectedEOFError",
    "JobNotFound",
    "WorkspaceNotSet",
    "NodeNotFound",
    "DatasetWriteError",
    "DatasetReadError",
    "SecretNotFound",
    "GroupConflict",
    "GroupNotFound",
    "DuplicateJobError",
    "DuplicateExperimentError",
    "TaskNotFound",
    "ChecksumFailedError",
    "TaskStoppedError",
    "JobFailedError",
    "JobTimeoutError",
    "ExperimentSpecError",
    "ThreadCanceledError",
]


class BeakerError(Exception):
    """
    Base class for all Beaker errors other than :exc:`HTTPError`, which is re-exported
    from :exc:`requests.exceptions.HTTPError`, and :exc:`ValidationError`, which is
    re-exported from `pydantic <https://pydantic-docs.helpmanual.io/>`_.
    """


class NotFoundError(BeakerError):
    """
    Base class for all "not found" error types.
    """


class AccountNotFound(NotFoundError):
    pass


class OrganizationNotFound(NotFoundError):
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


class ImageNotFound(NotFoundError):
    pass


class ImageConflict(BeakerError):
    """
    Raised when attempting to create/rename an image if an image by that name already exists.
    """


class WorkspaceNotFound(NotFoundError):
    pass


class WorkspaceWriteError(BeakerError):
    """
    Raised when attempting to modify or add to a workspace that's been archived.
    """


class WorkspaceConflict(BeakerError):
    """
    Raised when attempting to create/rename a workspace if a workspace by that name already exists.
    """


class ClusterNotFound(NotFoundError):
    pass


class ClusterConflict(BeakerError):
    """
    Raised when attempting to create a cluster if a cluster by that name already exists.
    """


class ExperimentNotFound(NotFoundError):
    pass


class ExperimentConflict(BeakerError):
    """
    Raised when attempting to create/rename an experiment if an experiment by that name already exists.
    """


class DatasetConflict(BeakerError):
    """
    Raised when attempting to create/rename a dataset if a dataset by that name already exists.
    """


class DatasetNotFound(NotFoundError):
    pass


class UnexpectedEOFError(BeakerError):
    """
    Raised when creating a dataset when an empty source file is encountered.
    """


class JobNotFound(NotFoundError):
    pass


class WorkspaceNotSet(BeakerError):
    """
    Raised when workspace argument is not provided and there is no default workspace set.
    """


class NodeNotFound(NotFoundError):
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


class SecretNotFound(NotFoundError):
    pass


class GroupConflict(BeakerError):
    """
    Raised when attempting to create/rename a group if a group by that name already exists.
    """


class GroupNotFound(NotFoundError):
    pass


class DuplicateJobError(BeakerError):
    """
    Raised when duplicate jobs are passed into a method that expects unique jobs.
    """


class DuplicateExperimentError(BeakerError):
    """
    Raised when duplicate experiments are passed into a method that expects unique experiments.
    """


class TaskNotFound(NotFoundError):
    pass


class ChecksumFailedError(BeakerError):
    """
    Raised when a downloaded file from a Beaker dataset is corrupted.
    """


class TaskStoppedError(BeakerError):
    def __init__(self, msg: Optional[str] = None, task: Optional[Task] = None):
        super().__init__(msg)
        self.task = task


class JobFailedError(BeakerError):
    def __init__(self, msg: Optional[str] = None, job: Optional[Job] = None):
        super().__init__(msg)
        self.job = job


class JobTimeoutError(BeakerError, TimeoutError):
    pass


class ExperimentSpecError(BeakerError):
    pass


class ThreadCanceledError(BeakerError):
    pass
