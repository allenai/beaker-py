# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with one exception: minor yet potentially breaking changes to the data model that are made to maintain
compatibility with the Beaker server and not necessarily given new major releases. We often
use patch releases for compatibility fixes instead.

## Unreleased

### Fixed

- Fixed bug where `Beaker.experiment.delete()` would fail if the result dataset was already
  deleted.

## [v1.6.5](https://github.com/allenai/beaker-py/releases/tag/v1.6.5) - 2022-07-15

### Fixed

- Fixed bug with checking job status. Sometimes a successful job would be marked as failed.

## [v1.6.4](https://github.com/allenai/beaker-py/releases/tag/v1.6.4) - 2022-07-14

### Fixed

- Removed outdated field `owner` from `Experiment`, `Task`, and `Dataset`.

## [v1.6.3](https://github.com/allenai/beaker-py/releases/tag/v1.6.3) - 2022-07-05

### Fixed

- Handling empty string values in Beaker config YAML files for compatibility with `beaker` CLI.
  Any empty string values in a Beaker config YAML file are now converted to `None` when the `Config`
  object is loaded from the file.
  On the other hand, if you try to explicitly set the value of a field to an empty string when initializing the `Beaker` client (e.g. `Beaker.from_env(default_org='')`)
  you'll get a `ValueError`.

## [v1.6.2](https://github.com/allenai/beaker-py/releases/tag/v1.6.2) - 2022-06-27

### Fixed

- Fixed a bug where the `session` parameter to `Beaker.from_env()` wasn't actually passed through to the class' `__init__()` method.

## [v1.6.1](https://github.com/allenai/beaker-py/releases/tag/v1.6.1) - 2022-06-24

### Changed

- Added support for older versions of Pydantic (back to v1.8.2).

## [v1.6.0](https://github.com/allenai/beaker-py/releases/tag/v1.6.0) - 2022-06-17

### Added

- Added `Beaker.job.follow()` and `Beaker.experiment.follow()` methods for live streaming logs.

### Changed

- The return type of `Beaker.experiment.tasks()` behaves like both a `Sequence[Task]` and a `Mapping[str, Task]`, i.e.
  you can call `__getitem__()` with either an `int`, `slice`, or a `str` for the name of a task.

### Fixed

- Fixed a bug where `Beaker.(job|experiment).(wait_for|as_completed)()` methods could hang if a job was canceled or failed to ever start for some reason.

## [v1.5.1](https://github.com/allenai/beaker-py/releases/tag/v1.5.1) - 2022-06-16

### Changed

- `Beaker.(job|experiment).(wait_for|as_completed)()` methods now raises a more specific `JobTimeoutError` (which inherits from `TimeoutError`) instead of a generic `TimeoutError`.

## [v1.5.0](https://github.com/allenai/beaker-py/releases/tag/v1.5.0) - 2022-06-16

### Added

- Added `since` parameter to `Beaker.job.logs()` and `Beaker.experiment.logs()`.

## [v1.4.2](https://github.com/allenai/beaker-py/releases/tag/v1.4.2) - 2022-06-13

### Fixed

- Fixed bug in loading config where encountering unknown fields would cause an exception.
  `beaker-py` now gracefully handles this.

## [v1.4.1](https://github.com/allenai/beaker-py/releases/tag/v1.4.1) - 2022-06-10

### Added

- Added `session` argument to `Beaker` client constructors (`.from_env()` and `__init__()`).
  You can use this argument to force the client to use a single HTTP `Session` for all requests to the server
  for the life of the client. Using this approach it's not necessary to use the `Beaker.session()` context manager,
  but you should only use this if the client is short-lived.

## [v1.4.0](https://github.com/allenai/beaker-py/releases/tag/v1.4.0) - 2022-06-09

### Added

- Added `Beaker.session()` context manager for improving performance when calling a series of 
  client methods in a row.
- Added `timeout` parameter to `Beaker` client initialization methods with a default of `5` (seconds).
  This controls the connect and read timeouts of HTTP requests sent to the Beaker server.

## [v1.3.0](https://github.com/allenai/beaker-py/releases/tag/v1.3.0) - 2022-05-31

### Added

- Added `Beaker.group.export_experiments()` method.

### Fixed

- Fixed `Job` priority validation.

## [v1.2.0](https://github.com/allenai/beaker-py/releases/tag/v1.2.0) - 2022-05-25

### Added

- Added `Beaker.dataset.file_info()` method.
- Added `.workspace` (`WorkspaceRef`) property to `Dataset`, `Image`, `Group`, and `Experiment`.
  This is just an alias for the `.workspace_ref` property.

### Changed

- `Beaker.dataset.stream_file()` now can also take a `FileInfo` object as the 2nd argument instead of a file path.
- `Digest` class is now hashable.

## [v1.1.0](https://github.com/allenai/beaker-py/releases/tag/v1.1.0) - 2022-05-18

### Added

- Added `ExperimentSpec.to_file()` method.

## [v1.0.0](https://github.com/allenai/beaker-py/releases/tag/v1.0.0) - 2022-05-13

### Removed

- Removed deprecated `Beaker.experiment.await_all()` method.

## [v0.15.3](https://github.com/allenai/beaker-py/releases/tag/v0.15.3) - 2022-05-10

### Added

- Added `Digest` type and changed type of `FileInfo.digest` from `str` to `Digest`.

## [v0.15.2](https://github.com/allenai/beaker-py/releases/tag/v0.15.2) - 2022-05-09

### Added

- Added `Beaker.experiment.latest_job()` method.
- Added `strict: bool` argument to `Beaker.(experiment|job).(wait_for|as_completed)` methods.
- Added `description` and `source_execution` fields to `Dataset`.
- Added `description` field to `Experiment`.
- Added `description` field to `Image`.
- Added `description` field to `Workspace`.

## [v0.15.1](https://github.com/allenai/beaker-py/releases/tag/v0.15.1) - 2022-05-06

### Added

- Docker images released with major and major+minor version tags in addition to full version tag.

## [v0.15.0](https://github.com/allenai/beaker-py/releases/tag/v0.15.0) - 2022-05-06

### Added

- Added `ExperimentSpec.with_description()`.
- Added `TaskSpec.with_image()`, `.with_result()`, `.with_context()`, `.with_name()`, `.with_command()`, and `.with_arguments()`.

### Changed

- Renamed `delete_results_dataset` param to `delete_results_datasets` in `Beaker.experiment.delete()`.
- Renamed `TaskSpec.with_data()` to `TaskSpec.with_dataset()`.

### Fixed

- Fixed bug with `Beaker.experiment.delete()` that would lead to a `ValueError` being raised when the experiment to delete has multiple tasks.

## [v0.14.1](https://github.com/allenai/beaker-py/releases/tag/v0.14.1) - 2022-05-05

### Changed

- Replaced `id: str` field of `ClusterUtilization` with `cluster: Cluster`. `id` is still available
  as a property for backwards compatibility.

## [v0.14.0](https://github.com/allenai/beaker-py/releases/tag/v0.14.0) - 2022-05-04

### Added

- Added `description` parameter to `Beaker.dataset.create()`, `Beaker.image.create()`, `Beaker.workspace.create()`.
- Added `public` parameter to `Beaker.workspace.create()`.

### Changed

- `Beaker.workspace.grant_permissions` now takes a `Permission` enum type instead of a raw string, but raw strings will still work.

## [v0.13.2](https://github.com/allenai/beaker-py/releases/tag/v0.13.2) - 2022-04-29

### Changed

- The `Beaker.account.name` property is now cached for performance reasons with a TTL cache.
- Renamed `Cluster.nodeCost` to `Cluster.node_cost` for consistency.
- Fixed some issues around mutable data models with properties that have different snake case vs lower camel case names.

## [v0.13.1](https://github.com/allenai/beaker-py/releases/tag/v0.13.1) - 2022-04-28

### Changed

- `Beaker.dataset.fetch()` and `Beaker.dataset.stream_file()` now verify the digest of the downloaded bytes
  against the expected digest by default. A `ChecksumFailedError` is raised if they don't match.
  You can skip validating the checksum by passing `validate_checksum=False`.
- Added a progress bar to `Beaker.dataset.stream_file()`. This can be disabled by passing `quiet=True`.

## [v0.13.0](https://github.com/allenai/beaker-py/releases/tag/v0.13.0) - 2022-04-27

### Added

- Added `Beaker.dataset.url()` method.
- Added `Beaker.image.url()` method.
- Added `Beaker.group.url()` method.
- Added `Beaker.workspace.url()` method.
- Added `Beaker.cluster.url()` method.

### Changed

- Improved performance of `Beaker.cluster.filter_available()` by using a `ThreadPoolExecutor` for concurrency.
- Changed behavior of `Beaker.dataset.create()` and `Beaker.dataset.sync()` with respect to source files. By default now, source files and directories will be uploading as their given path, instead of just their name. You can still get the old behavior by passing `strip_paths=True`.
- Changed default value of `max_workers` to `None` in `Beaker.dataset.create()` and `.sync()`.
  When left as `None`, the number of workers will be determined by the [`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor).
- "." now allowed in beaker names.

## [v0.12.0](https://github.com/allenai/beaker-py/releases/tag/v0.12.0) - 2022-04-26

### Added

- Added FAQ section to the docs.
- All data models are now hashable and faux immutable, and use tuples instead of lists.
- Added `delete_results_dataset: bool = True` parameter to `Beaker.experiment.delete()`.
- Added `Cluster.is_cloud` and `Cluster.is_active` properties.

### Changed

- Changed the return type of `Beaker.cluster.filter_available()` from `List[Cluster]` to
  `List[ClusterUtilization]`.
- Renamed and consolidated `NodeSpec` and `NodeShape` to `NodeResources`.

## [v0.11.0](https://github.com/allenai/beaker-py/releases/tag/v0.11.0) - 2022-04-21

### Added

- Added `Task.latest_job` property.

### Changed

- Changed signature of `Beaker.experiment.(logs|metrics|results)` methods: replaced parameter
  `task_name: Optional[str]` with `task: Optional[Union[str, Task]]`.

## [v0.10.0](https://github.com/allenai/beaker-py/releases/tag/v0.10.0) - 2022-04-20

### Added

- Added `Beaker.image.rename()` method.
- Added `Beaker.image.pull()` method.
- Added `Beaker.experiment.url()` method.

### Changed

- Changed return type of `Beaker.cluster.utilization()` to `ClusterUtilization`.

## [v0.9.0](https://github.com/allenai/beaker-py/releases/tag/v0.9.0) - 2022-04-19

### Added

- Added `Beaker.group` client and methods.
- Added `Beaker.workspace.groups()` method.
- Added `Beaker.experiment.resume()` method.
- Added `Beaker.experiment.metrics()` method.
- Added `Beaker.job.metrics()` method.
- Added `Beaker.job.results()` method.
- Added `Beaker.job.wait_for()` method.
- Added `Beaker.job.as_completed()` method.
- Added `Beaker.experiment.as_completed()` method.
- Added `Beaker.image.commit()` method.
- Added `commit` parameter to `Beaker.image.create()`.

### Changed

- Changed the signature of `Beaker.experiment.results()`. Added the `task_name` parameter
  and changed the return type to `Optional[Dataset]`.
- Changed the signature of `Beaker.experiment.logs()`. Removed the `job_id` parameter
  and added the `task_name` parameter.
- Deprecated `Beaker.experiment.await_all()`. Use `Beaker.experiment.wait_for()` instead.

### Fixed

- Fixed bug with `Beaker.image.create()`.

## [v0.8.4](https://github.com/allenai/beaker-py/releases/tag/v0.8.4) - 2022-04-18

### Fixed

- Fixed issue in data model for `Experiment`. `name` and `full_name` are now optional.
- Fixed issue in data model for `Image`. `name` and `full_name` are now optional.

## [v0.8.3](https://github.com/allenai/beaker-py/releases/tag/v0.8.3) - 2022-04-14

### Added

- Added `Beaker.workspace.(get|set|grant|revoke)_permissions()` and `.set_visibility()` methods.

### Changed

- Added better support for referencing Beaker items (images, experiments, datasets, etc)
  by their short name (without workspace, org, or account prefix) when the full name
  or ID can be assumed.
- Improved error documentation.

## [v0.8.2](https://github.com/allenai/beaker-py/releases/tag/v0.8.2) - 2022-04-13

### Added

- Implemented `Beaker.workspace.archive()`, `.unarchive()`, `.rename()`, `.move()`, and `create()` methods.
- Implemented `Beaker.job.stop()` and `Beaker.job.finalize()` methods.
- Added `WorkspaceWriteError` for when you attempt to write to an archived workspace. Before this
  would just result in an `HTTPError` with a 403 status code.

### Changed

- Allowed using workspace name without organization when `Config.default_org` is set.
  Otherwise `OrganizationNotSet` error is raised.

## [v0.8.1](https://github.com/allenai/beaker-py/releases/tag/v0.8.1) - 2022-04-12

### Added

- Implemented `__str__` method on `Beaker` client for debugging.
- Improved documentation for `ExperimentSpec`, `TaskSpec`, and other related data models,
  and added new convenience constructors such as `TaskSpec.new()`.

### Changed

- Changed default spec version to `v2`.

### Fixed

- Improved experiment spec validation in `Beaker.experiment.create()` to raise more specific error types.

## [v0.8.0](https://github.com/allenai/beaker-py/releases/tag/v0.8.0) - 2022-04-12

### Changed

- `Beaker.experiment.await_all()` now takes a variable number of experiments and returns a list
  with the same length and order of the finished experiments.

### Fixed

- Fixed bug where `Beaker.experiment.create()` would fail with an `HTTPError` if the image
  in the spec doesn't exist. Now this will fail with `ImageNotFound`.

## [v0.7.0](https://github.com/allenai/beaker-py/releases/tag/v0.7.0) - 2022-04-11

### Changed

- Made `org` parameter optional, defaulting to `Config.default_org`.

### Fixed

- Fixed the behavior of some methods that take a `workspace` parameter. Previously, if the workspace
  didn't exist, it would be silently created. Now a `WorkspaceNotFound` error is raised.

## [v0.6.1](https://github.com/allenai/beaker-py/releases/tag/v0.6.1) - 2022-04-11

### Added

- Added `Beaker.workspace.secrets()`.
- Added `Beaker.secret.get()`.
- Added `Beaker.secret.read()`.
- Added `Beaker.secret.write()`.
- Added `Beaker.secret.delete()`.

## [v0.6.0](https://github.com/allenai/beaker-py/releases/tag/v0.6.0) - 2022-04-11

### Added

- Added `Beaker.experiment.rename()`.
- Added `Beaker.experiment.tasks()`.
- Added `Beaker.experiment.results()`.
- Added `Beaker.experiment.spec()`.
- Added `Beaker.workspace.datasets()`.
- Added `Beaker.workspace.experiments()`.
- Added `Beaker.workspace.images()`.
- Added `Beaker.workspace.list()`.
- Added `Beaker.account.get()`.

### Removed

- Removed `Beaker.experiment.list()`. Please use `Beaker.workspace.experiments()` instead.

## [v0.5.5](https://github.com/allenai/beaker-py/releases/tag/v0.5.5) - 2022-04-10

### Added

- Added `callback` parameter to `Beaker.experiment.await_all()`.

## [v0.5.4](https://github.com/allenai/beaker-py/releases/tag/v0.5.4) - 2022-04-10

### Added

- Added `Beaker.dataset.size()`.
- Added `Beaker.dataset.rename()`.
- Added `ExperimentSpec.from_file()`.
- Added `Beaker.cluster.filter_available()`.

## [v0.5.3](https://github.com/allenai/beaker-py/releases/tag/v0.5.3) - 2022-04-08

### Added

- Added `Beaker.dataset.commit()`.
- Added `Beaker.dataset.ls()`.
- Added `Beaker.dataset.stream_file()`.

### Changed

- Changed behavior of `target` parameter in `Beaker.dataset.create()`. It now always represents the name of a directory.
- Changed the signature of `Beaker.dataset.create()`. It now accepts a variable number of source files or directories.

## [v0.5.2](https://github.com/allenai/beaker-py/releases/tag/v0.5.2) - 2022-04-07

### Added

- Added `Beaker.experiment.stop()`.

### Fixed

- Fixed bug with `Beaker.experiment.await_all()`.

## [v0.5.1](https://github.com/allenai/beaker-py/releases/tag/v0.5.1) - 2022-04-07

### Fixed

- Fixed bug with `Beaker.jobs.list()`.

## [v0.5.0](https://github.com/allenai/beaker-py/releases/tag/v0.5.0) - 2022-04-07

### Added

- Added `Beaker.node` service client.
- Added `Beaker.job.get()` and `Beaker.job.list()` methods.
- Added `Beaker.cluster.utilization()`.

### Fixed

- Fixed warning about newer version.

### Removed

- Removed `Execution` data model, since it's deprecated and redundant with `Job`.

## [v0.4.3](https://github.com/allenai/beaker-py/releases/tag/v0.4.3) - 2022-04-06

### Added

- Added `Beaker.account.name` property and `Beaker.account.list_organizations()` method.
- Added `ExperimentSpec` and all components to the data model.
- Added `Beaker.cluster` service client for managing Beaker clusters.
- Added `Beaker.organization` service client for managing Beaker organizations.

### Changed

- `Beaker.experiment.create()` now accepts either an `ExperimentSpec` instance or the path to a YAML spec file.

## [v0.4.2](https://github.com/allenai/beaker-py/releases/tag/v0.4.2) - 2022-04-04

### Added

- Added support for large files with `Beaker.dataset.create()`.
- Added `Beaker.dataset.fetch()`.

## [v0.4.1](https://github.com/allenai/beaker-py/releases/tag/v0.4.1) - 2022-04-03

### Added

- Added `Beaker.experiment.delete()` and `Beaker.experiment.await_all()` methods.
- `Beaker.dataset.create` can now handle directories.

## [v0.4.0](https://github.com/allenai/beaker-py/releases/tag/v0.4.0) - 2022-04-03

### Changed

- Breaking changs to `Beaker` client API. Methods for services have been split up into seperate service clients. For example, previously you would create an image with `beaker.create_image()`, whereas now you would do `beaker.image.create()`.

## [v0.3.9](https://github.com/allenai/beaker-py/releases/tag/v0.3.9) - 2022-04-01

### Fixed

- Fixed bug in `delete_image()` that would result in `ImageNotFound` error when using image full name instead of ID.

## [v0.3.8](https://github.com/allenai/beaker-py/releases/tag/v0.3.8) - 2022-04-01

### Changed

- All `Beaker` client methods now return strongly typed data models.
- Replaced old progress diplays with prettier diplays from `rich`.

## [v0.2.8](https://github.com/allenai/beaker-py/releases/tag/v0.2.8) - 2022-03-31

### Fixed

- Fixed getting experiment from name.

## [v0.2.7](https://github.com/allenai/beaker-py/releases/tag/v0.2.7) - 2022-03-31

### Added

- Added `Beaker.create_dataset()` method.

## [v0.2.6](https://github.com/allenai/beaker-py/releases/tag/v0.2.6) - 2022-01-19

### Added

- Added `list_experiments()` method.

## [v0.2.5](https://github.com/allenai/beaker-py/releases/tag/v0.2.5) - 2021-12-14

### Fixed

- Fixed bug where `Beaker.from_env()` would fail with missing `BEAKER_TOKEN` even if you passed the token to the method.

## [v0.2.4](https://github.com/allenai/beaker-py/releases/tag/v0.2.4) - 2021-12-09

### Changed

- Docker Client is initialized lazily so that some functionality of `Beaker` client can be used on systems without Docker.

## [v0.2.3](https://github.com/allenai/beaker-py/releases/tag/v0.2.3) - 2021-12-09

### Fixed

- Fixed crash that could occur when `$HOME` directory doesn't exist.

## [v0.2.2](https://github.com/allenai/beaker-py/releases/tag/v0.2.2) - 2021-12-08

## [v0.2.1](https://github.com/allenai/beaker-py/releases/tag/v0.2.1) - 2021-12-08

### Fixed

- Fixed bug with `Config.save()`.
- Fixed bug with `create_image()` where it would fail if workspace doesn't exist yet.

## [v0.2.0](https://github.com/allenai/beaker-py/releases/tag/v0.2.0) - 2021-12-07

### Added

- Added many new methods.
- Added `beaker.exceptions` module.

### Changed

- Several breaking changes to `Beaker` method names.

## [v0.1.0](https://github.com/allenai/beaker-py/releases/tag/v0.1.0) - 2021-11-19

### Added

- Added `Beaker` client class.
