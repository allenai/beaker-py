from pydantic import ValidationError  # noqa: F401, re-imported here for convenience
from requests.exceptions import (  # noqa: F401, re-imported here for convenience
    HTTPError,
)


class BeakerError(Exception):
    """
    Base class for all Beaker errors other than :exc:`HTTPError`, which is re-exported
    from :exc:`requests.exceptions.HTTPError`, and :exc:`ValidationError`, which is
    re-exported from `pydantic <https://pydantic-docs.helpmanual.io/>`_.
    """


class ConfigurationError(BeakerError):
    pass


class ImageNotFound(BeakerError):
    pass


class ImageConflict(BeakerError):
    """
    Raised when attempting to create an image if an image by that name already exists.
    """


class WorkspaceNotFound(BeakerError):
    pass


class ExperimentNotFound(BeakerError):
    pass


class ExperimentConflict(BeakerError):
    """
    Raised when attempting to create an experiment if an experiment by that name already exists.
    """


class DatasetConflict(BeakerError):
    """
    Raised when attempting to create a dataset if a dataset by that name already exists.
    """


class DatasetNotFound(BeakerError):
    pass


class JobNotFound(BeakerError):
    pass


class WorkspaceNotSet(BeakerError):
    """
    Raised when workspace argument is not provided and there is no default workspace set.
    """
