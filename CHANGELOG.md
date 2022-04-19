# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Added `Beaker.group` client and methods.
- Added `Beaker.workspace.groups()` method.
- Added `Beaker.experiment.resume()` method.
- Added `Beaker.experiment.metrics()` method.
- Added `Beaker.job.metrics()` method.
- Added `Beaker.job.results()` method.
- Added `Beaker.job.await_all()` method.

### Changed

- Changed the signature of `Beaker.experiment.results()`. Added the `task_name` parameter
  and changed the return type to `Optional[Dataset]`.
- Changed the signature of `Beaker.experiment.logs()`. Removed the `job_id` parameter
  and added the `task_name` parameter.

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
