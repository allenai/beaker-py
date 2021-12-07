from requests.exceptions import HTTPError  # re-imported here for convenience


class BeakerError(Exception):
    """
    Base class for all Beaker errors other than :exc:`HTTPError` which is re-exported
    from :exc:`requests.exceptions.HTTPError`.
    """


class ImageNotFound(BeakerError):
    pass


class ImageConflict(BeakerError):
    pass


class WorkspaceNotFound(BeakerError):
    pass


class ExperimentNotFound(BeakerError):
    pass


class ExperimentConflict(BeakerError):
    pass


class DatasetNotFound(BeakerError):
    pass


class JobNotFound(BeakerError):
    pass
