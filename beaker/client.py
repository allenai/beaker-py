import json
import os
import time
import urllib.parse
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Deque, Dict, Generator, List, Optional, Union

import docker
import requests
from cachetools import TTLCache, cached
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from rich.progress import (
    BarColumn,
    FileSizeColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .config import Config
from .data_model import *
from .exceptions import *
from .util import BufferedReaderWithProgress, DownloadUploadColumn
from .version import VERSION

__all__ = ["Beaker"]


PathOrStr = Union[os.PathLike, str]


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
        self._workspace = WorkspaceClient(self)
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
    def account(self) -> "AccountClient":
        """
        Manage accounts.
        """
        return self._account

    @property
    def workspace(self) -> "WorkspaceClient":
        """
        Manage workspaces.
        """
        return self._workspace

    @property
    def dataset(self) -> "DatasetClient":
        """
        Manage datasets.
        """
        return self._dataset

    @property
    def image(self) -> "ImageClient":
        """
        Manage images.
        """
        return self._image

    @property
    def job(self) -> "JobClient":
        """
        Manage jobs.
        """
        return self._job

    @property
    def experiment(self) -> "ExperimentClient":
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


class ServiceClient:
    RECOVERABLE_SERVER_ERROR_CODES = (502, 503, 504)
    MAX_RETRIES = 5
    API_VERSION = "v3"

    def __init__(self, beaker: Beaker):
        self.beaker = beaker
        self._base_url = f"{self.config.agent_address}/api/{self.API_VERSION}"

    @property
    def config(self) -> Config:
        return self.beaker.config

    @property
    def docker(self) -> docker.DockerClient:
        return self.beaker.docker

    @contextmanager
    def _session_with_backoff(self) -> Generator[requests.Session, None, None]:
        session = requests.Session()
        retries = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=self.RECOVERABLE_SERVER_ERROR_CODES,
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        yield session

    def request(
        self,
        resource: str,
        method: str = "GET",
        query: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        exceptions_for_status: Optional[Dict[int, BeakerError]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        stream: bool = False,
    ) -> requests.Response:
        with self._session_with_backoff() as session:
            url = f"{base_url or self._base_url}/{resource}"
            if query is not None:
                url = url + "?" + urllib.parse.urlencode(query)
            default_headers = {
                "Authorization": f"Bearer {token or self.config.user_token}",
                "Content-Type": "application/json",
                "User-Agent": f"beaker-py v{VERSION}",
            }
            if headers is not None:
                default_headers.update(headers)
            response = getattr(session, method.lower())(
                url,
                headers=default_headers,
                data=json.dumps(data) if isinstance(data, dict) else data,
                stream=stream,
            )
            if exceptions_for_status is not None and response.status_code in exceptions_for_status:
                raise exceptions_for_status[response.status_code]
            response.raise_for_status()
            return response

    def _resolve_workspace(self, workspace: Optional[str], ensure_exists: bool = True) -> str:
        workspace_name = workspace or self.config.default_workspace
        if workspace_name is None:
            raise WorkspaceNotSet("'workspace' argument required since default workspace not set")
        else:
            if ensure_exists:
                self.beaker.workspace.ensure(workspace_name)
            return workspace_name

    def _url_quote(self, id: str) -> str:
        return urllib.parse.quote(id, safe="")


class AccountClient(ServiceClient):
    @cached(cache=TTLCache(maxsize=10, ttl=5 * 60))
    def whoami(self) -> Account:
        """
        Check who you are authenticated as.
        """
        return Account.from_json(self.request("user").json())


class WorkspaceClient(ServiceClient):
    @cached(cache=TTLCache(maxsize=10, ttl=5 * 60))
    def get(self, workspace: Optional[str] = None) -> Workspace:
        """
        Get information about the workspace.

        :param workspace: The workspace name. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return Workspace.from_json(
            self.request(
                f"workspaces/{urllib.parse.quote(workspace_name, safe='')}",
                exceptions_for_status={
                    404: WorkspaceNotFound(self._not_found_err_msg(workspace_name))
                },
            ).json()
        )

    def ensure(self, workspace: str):
        """
        Ensure that the given workspace exists.

        :param workspace: The full workspace name.

        :raises HTTPError: Any other HTTP exception that can occur.
        :raises ValueError: If the workspace name is invalid.

        """
        try:
            self.get(workspace)
        except WorkspaceNotFound:
            try:
                org, name = workspace.split("/")
            except ValueError:
                raise ValueError(f"Invalided workspace name '{workspace}'")
            self.request("workspaces", method="POST", data={"name": name, "org": org})

    def _not_found_err_msg(self, workspace: str) -> str:
        return (
            f"'{workspace}': Make sure you're using the *full* name of the workspace "
            f"(with the account prefix, e.g. 'username/workspace_name')"
        )


class DatasetClient(ServiceClient):
    HEADER_UPLOAD_ID = "Upload-ID"
    HEADER_UPLOAD_LENGTH = "Upload-Length"
    HEADER_UPLOAD_OFFSET = "Upload-Offset"
    HEADER_DIGEST = "Digest"

    SHA256 = "SHA256"

    REQUEST_SIZE_LIMIT = 32 * 1024 * 1024

    def create(
        self,
        name: str,
        source: PathOrStr,
        target: Optional[PathOrStr] = None,
        workspace: Optional[str] = None,
        force: bool = False,
        max_workers: int = 8,
        quiet: bool = False,
    ) -> Dataset:
        """
        Create a dataset with the source file(s).

        :param name: The name to assign to the new dataset.
        :param source: The local source file or directory of the dataset.
        :param target: If ``source`` is a file, you can change the name of the file in the dataset
            by specifying ``target``. If ``source`` is a directory, you can set ``target`` to
            specify a directory in the dataset to upload ``source`` under.
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param force: If ``True`` and a dataset by the given name already exists, it will be overwritten.
        :param max_workers: The maximum number of thread pool workers to use to upload files concurrently.
        :param quiet: If ``True``, progress won't be displayed.

        :raises DatasetConflict: If a dataset by that name already exists and ``force=False``.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        :raises UnexpectedEOFError: If ``source`` is a single empty file, or if ``source`` is a directory and
            the contents of one of the directories files is changed while creating the dataset.
        :raises FileNotFoundError: If the ``source`` doesn't exist.
        """
        workspace_name = self._resolve_workspace(workspace)

        # Ensure source exists.
        source: Path = Path(source)
        if not source.exists():
            raise FileNotFoundError(str(source))

        # Create the dataset.
        def make_dataset() -> Dataset:
            return Dataset.from_json(
                self.request(
                    "datasets",
                    method="POST",
                    query={"name": name},
                    data={"workspace": workspace_name, "fileheap": True},
                    exceptions_for_status={409: DatasetConflict(name)},
                ).json()
            )

        try:
            dataset_info = make_dataset()
        except DatasetConflict:
            if force:
                self.delete(f"{self.beaker.account.whoami().name}/{name}")
                dataset_info = make_dataset()
            else:
                raise
        assert dataset_info.storage is not None

        # Upload the file(s).
        self._sync_source(dataset_info, source, target, quiet=quiet, max_workers=max_workers)

        # Commit the dataset.
        self.request(
            f"datasets/{dataset_info.id}",
            method="PATCH",
            data={"commit": True},
        )

        # Return info about the dataset.
        return self.get(dataset_info.id)

    def fetch(
        self,
        dataset: str,
        target: Optional[PathOrStr] = None,
        force: bool = False,
        max_workers: int = 8,
        quiet: bool = False,
    ):
        """
        Download a dataset.

        :param dataset: The dataset ID, full name, or object.
        :param target: The target path to fetched data. Defaults to ``Path(.)``.
        :param max_workers: The maximum number of thread pool workers to use to download files concurrently.
        :param force: If ``True``, existing local files will be overwritten.
        :param quiet: If ``True``, progress won't be displayed.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises FileExistsError: If ``force=False`` and an existing local file clashes with a file
            in the Beaker dataset.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.get(dataset)
        assert dataset.storage is not None

        storage_info = DatasetStorageInfo.from_json(
            self.request(
                f"datasets/{dataset.storage.id}",
                method="GET",
                token=dataset.storage.token,
                base_url=dataset.storage.address,
            ).json()
        )

        target: Path = Path(target or Path("."))
        target.mkdir(exist_ok=True, parents=True)

        total_bytes_to_download: Optional[int] = None
        total_downloaded: int = 0
        progress_columns: List[Union[str, ProgressColumn]]
        if storage_info.size is not None and storage_info.size.final:
            total_bytes_to_download = storage_info.size.bytes
            progress_columns = [
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                DownloadUploadColumn(),
            ]
        else:
            progress_columns = [
                "[progress.description]{task.description}",
                SpinnerColumn(),
                TimeElapsedColumn(),
                DownloadUploadColumn(),
            ]

        with Progress(*progress_columns, disable=quiet) as progress:
            bytes_task = progress.add_task("Downloading dataset")
            if total_bytes_to_download is not None:
                progress.update(bytes_task, total=total_bytes_to_download)

            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                download_futures = []
                for file_info in self._iter_files(dataset.storage):
                    if total_bytes_to_download is None:
                        progress.update(bytes_task, total=total_downloaded + file_info.size + 1)
                    target_path = target / Path(file_info.path)
                    if not force and target_path.exists():
                        raise FileExistsError(file_info.path)
                    future = executor.submit(
                        self._download_file, file_info, target_path, progress, bytes_task
                    )
                    download_futures.append(future)

                for future in concurrent.futures.as_completed(download_futures):
                    total_downloaded += future.result()

            if total_bytes_to_download is None:
                progress.update(bytes_task, total=total_downloaded, completed=total_downloaded)

    def get(self, dataset: str) -> Dataset:
        """
        Get info about a dataset.

        :param dataset: The dataset ID or full name.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        return Dataset.from_json(
            self.request(
                f"datasets/{urllib.parse.quote(dataset, safe='')}",
                exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset))},
            ).json()
        )

    def delete(self, dataset: Union[str, Dataset]):
        """
        Delete a dataset.

        :param dataset: The dataset ID, full name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset_id = dataset if isinstance(dataset, str) else dataset.id
        self.request(
            f"datasets/{self._url_quote(dataset_id)}",
            method="DELETE",
            exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset_id))},
        )

    def _not_found_err_msg(self, dataset: str) -> str:
        return (
            f"'{dataset}': Make sure you're using a valid Beaker dataset ID or the "
            f"*full* name of the dataset (with the account prefix, e.g. 'username/dataset_name')"
        )

    def _sync_source(
        self,
        dataset: Dataset,
        source: PathOrStr,
        target: Optional[PathOrStr] = None,
        quiet: bool = False,
        max_workers: int = 8,
    ) -> None:
        source: Path = Path(source)

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            DownloadUploadColumn(),
            disable=quiet,
        ) as progress:
            bytes_task = progress.add_task("Uploading dataset")
            if source.is_file():
                size = source.lstat().st_size
                if size == 0:
                    raise UnexpectedEOFError(str(source))
                progress.update(bytes_task, total=size)
                total_uploaded = self._upload_file(
                    dataset, size, source, target or source.name, progress, bytes_task
                )
                progress.update(bytes_task, total=total_uploaded)
            elif source.is_dir():
                import concurrent.futures

                # Gather all files to upload and count the total number of bytes.
                total_bytes = 0
                path_to_size: Dict[Path, int] = {}
                for path in source.glob("**/*"):
                    if path.is_dir():
                        continue
                    size = path.lstat().st_size
                    if size == 0:
                        continue
                    path_to_size[path] = size
                    total_bytes += size
                progress.update(bytes_task, total=total_bytes)

                # Now upload.
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Dispatch tasks to thread pool executor.
                    future_to_path = {}
                    for path, size in path_to_size.items():
                        target_path = path.relative_to(source)
                        if target is not None:
                            target_path = Path(target) / target_path
                        future = executor.submit(
                            self._upload_file,
                            dataset,
                            size,
                            path,
                            target_path,
                            progress,
                            bytes_task,
                            True,
                        )
                        future_to_path[future] = path

                    # Collect completed tasks.
                    for future in concurrent.futures.as_completed(future_to_path):
                        path = future_to_path[future]
                        original_size = path_to_size[path]
                        actual_size = future.result()
                        if actual_size != original_size:
                            # If the size of the file has changed since we started, adjust total.
                            total_bytes += actual_size - original_size
                            progress.update(bytes_task, total=total_bytes)
            else:
                raise FileNotFoundError(source)

    def _upload_file(
        self,
        dataset: Dataset,
        size: int,
        source: PathOrStr,
        target: PathOrStr,
        progress: Progress,
        task_id: TaskID,
        ignore_errors: bool = False,
    ) -> int:
        source: Path = Path(source)
        assert dataset.storage is not None
        if ignore_errors and not source.exists():
            return 0

        with source.open("rb") as source_file:
            source_file_wrapper = BufferedReaderWithProgress(source_file, progress, task_id)
            body: Optional[BufferedReaderWithProgress] = source_file_wrapper
            digest: Optional[bytes] = None

            if size > self.REQUEST_SIZE_LIMIT:
                response = self.request(
                    "uploads",
                    method="POST",
                    token=dataset.storage.token,
                    base_url=dataset.storage.address,
                )
                upload_id = response.headers[self.HEADER_UPLOAD_ID]

                written = 0
                while written < size:
                    chunk = source_file_wrapper.read(self.REQUEST_SIZE_LIMIT)
                    if not chunk:
                        break
                    response = self.request(
                        f"uploads/{upload_id}",
                        method="PATCH",
                        data=chunk,
                        token=dataset.storage.token,
                        base_url=dataset.storage.address,
                        headers={
                            self.HEADER_UPLOAD_LENGTH: str(size),
                            self.HEADER_UPLOAD_OFFSET: str(written),
                        },
                    )
                    written += len(chunk)

                    encoded_digest = response.headers.get(self.HEADER_DIGEST)
                    if encoded_digest:
                        digest = self._decode_digest(encoded_digest)
                        break

                if written != size:
                    raise UnexpectedEOFError(str(source))

                body = None

            self.request(
                f"datasets/{dataset.storage.id}/files/{str(target)}",
                method="PUT",
                data=body,
                token=dataset.storage.token,
                base_url=dataset.storage.address,
                headers=None if not digest else {self.HEADER_DIGEST: self._encode_digest(digest)},
                stream=body is not None,
            )

            return source_file_wrapper.total_read

    def _encode_digest(self, digest: bytes) -> str:
        import base64

        return f"{self.SHA256} {base64.standard_b64encode(digest).decode()}"

    def _decode_digest(self, encoded_digest: str) -> bytes:
        import base64

        _, encoded = encoded_digest.split(" ", 2)
        return base64.standard_b64decode(encoded)

    def _iter_files(self, storage: DatasetStorage) -> Generator[FileInfo, None, None]:
        from collections import deque

        files: Deque[FileInfo] = deque([])
        last_request: bool = False
        cursor: Optional[str] = ""
        while files or not last_request:
            if files:
                yield files.popleft()
            else:
                manifest = DatasetManifest.from_json(
                    self.request(
                        f"datasets/{storage.id}/manifest",
                        method="GET",
                        token=storage.token,
                        base_url=storage.address,
                        query={"cursor": cursor, "path": "", "url": True},
                    ).json()
                )
                files.extend(manifest.files)
                cursor = manifest.cursor
                if not cursor:
                    last_request = True

    def _download_file(
        self, file_info: FileInfo, target_path: Path, progress: Progress, task_id: TaskID
    ) -> int:
        import tempfile

        total_bytes = 0
        target_dir = target_path.parent
        target_dir.mkdir(exist_ok=True, parents=True)
        with self._session_with_backoff() as session:
            response = session.get(file_info.url, stream=True)
            response.raise_for_status()
            tmp_target = tempfile.NamedTemporaryFile(
                "w+b", dir=target_dir, delete=False, suffix=".tmp"
            )
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    total_bytes += len(chunk)
                    tmp_target.write(chunk)
                    progress.update(task_id, advance=len(chunk))
                os.replace(tmp_target.name, target_path)
            finally:
                tmp_target.close()
                if os.path.exists(tmp_target.name):
                    os.remove(tmp_target.name)
        return total_bytes


class ImageClient(ServiceClient):
    def create(
        self,
        name: str,
        image_tag: str,
        workspace: Optional[str] = None,
        quiet: bool = False,
    ) -> Image:
        """
        Upload a Docker image to Beaker.

        :param name: The name to assign to the image on Beaker.
        :param image_tag: The tag of the local image you're uploading.
        :param workspace: The workspace to upload the image to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ImageConflict: If an image with the given name already exists.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace)

        # Get local Docker image object.
        image = self.docker.images.get(image_tag)

        # Create new image on Beaker.
        image_data = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace_name, "ImageID": image.id, "ImageTag": image_tag},
            query={"name": name},
            exceptions_for_status={409: ImageConflict(name)},
        ).json()

        # Get the repo data for the Beaker image.
        repo_data = self.request(
            f"images/{image_data['id']}/repository", query={"upload": True}
        ).json()
        auth = repo_data["auth"]

        # Tag the local image with the new tag for the Beaker image.
        image.tag(repo_data["imageTag"])

        # Push the image to Beaker.
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            DownloadUploadColumn(),
            disable=quiet,
        ) as progress:
            layer_id_to_task: Dict[str, TaskID] = {}
            for line in self.docker.api.push(
                repo_data["imageTag"],
                stream=True,
                decode=True,
                auth_config={
                    "username": auth["user"],
                    "password": auth["password"],
                    "server_address": auth["server_address"],
                },
            ):
                if "id" not in line or "status" not in line:
                    continue
                layer_id = line["id"]
                status = line["status"].lower()
                progress_detail = line.get("progressDetail")
                task_id: TaskID
                if layer_id not in layer_id_to_task:
                    task_id = progress.add_task(layer_id, start=True, total=1)
                    layer_id_to_task[layer_id] = task_id
                else:
                    task_id = layer_id_to_task[layer_id]
                if status in {"preparing", "waiting"}:
                    progress.update(
                        task_id, total=1, completed=0, description=f"{layer_id}: {status.title()}"
                    )
                elif status == "pushing" and progress_detail:
                    progress.update(
                        task_id,
                        total=progress_detail["total"],
                        completed=progress_detail["current"],
                        description=f"{layer_id}: Pushing",
                    )
                elif status == "pushed":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Push complete"
                    )
                elif status == "layer already exists":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Already exists"
                    )
                else:
                    raise ValueError(f"unhandled status '{status}' ({line})")

        # Commit changes to Beaker.
        self.request(f"images/{image_data['id']}", method="PATCH", data={"Commit": True})

        # Return info about the Beaker image.
        return self.get(image_data["id"])

    def get(self, image: str) -> Image:
        """
        Get info about an image on Beaker.

        :param image: The Beaker image ID or full name.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        return Image.from_json(
            self.request(
                f"images/{self._url_quote(image)}",
                exceptions_for_status={404: ImageNotFound(self._not_found_err_msg(image))},
            ).json()
        )

    def delete(self, image: Union[str, Image]):
        """
        Delete an image on Beaker.

        :param image: The Beaker image ID, full name, or object.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        image_id = image if isinstance(image, str) else image.id
        self.request(
            f"images/{self._url_quote(image_id)}",
            method="DELETE",
            exceptions_for_status={404: ImageNotFound(self._not_found_err_msg(image_id))},
        )

    def _not_found_err_msg(self, image: str) -> str:
        return (
            f"'{image}': Make sure you're using a valid Beaker image ID or the "
            f"*full* name of the image (with the account prefix, e.g. 'username/image_name')"
        )


class JobClient(ServiceClient):
    def logs(self, job_id: str, quiet: bool = False) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. seealso::
            :meth:`Beaker.experiment.logs() <ExperimentClient.logs>`

        :param job_id: The ID of the Beaker job.
        :param quiet: If ``True``, progress won't be displayed.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        response = self.request(
            f"jobs/{job_id}/logs",
            exceptions_for_status={404: JobNotFound(job_id)},
            stream=True,
        )

        # TODO: currently beaker doesn't provide the Content-Length header, update this if they do.
        #  content_length = response.headers.get("Content-Length")
        #  total = int(content_length) if content_length is not None else None

        with Progress(
            "[progress.description]{task.description}",
            SpinnerColumn(),
            FileSizeColumn(),
            TimeElapsedColumn(),
            disable=quiet,
        ) as progress:
            task_id = progress.add_task("Downloading:")
            total = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    advance = len(chunk)
                    total += advance
                    progress.update(task_id, total=total + 1, advance=advance)
                    yield chunk


class ExperimentClient(ServiceClient):
    def create(
        self, name: str, spec: Dict[str, Any], workspace: Optional[str] = None
    ) -> Experiment:
        """
        Create a new Beaker experiment with the given ``spec``.

        :param name: The name to assign the experiment.
        :param spec: A Beaker `experiment spec
            <https://github.com/beaker/docs/blob/main/docs/concept/experiments.md#spec-format>`_
            in the form of a Python dictionary.
        :param workspace: The workspace to create the experiment under. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises ExperimentConflict: If an experiment with the given name already exists.
        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        workspace_name = self._resolve_workspace(workspace)
        experiment_data = self.request(
            f"workspaces/{self._url_quote(workspace_name)}/experiments",
            method="POST",
            query={"name": name},
            data=spec,
            exceptions_for_status={409: ExperimentConflict(name)},
        ).json()
        return self.get(experiment_data["id"])

    def get(self, experiment: str) -> Experiment:
        """
        Get info about an experiment.

        :param experiment: The experiment ID or full name.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        return Experiment.from_json(
            self.request(
                f"experiments/{self._url_quote(experiment)}",
                exceptions_for_status={
                    404: ExperimentNotFound(self._not_found_err_msg(experiment))
                },
            ).json()
        )

    def delete(self, experiment: Union[str, Experiment]):
        """
        Delete an experiment.

        :param experiment: The experiment ID, full name, or object.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        experiment_id = experiment if isinstance(experiment, str) else experiment.id
        self.request(
            f"experiments/{self._url_quote(experiment_id)}",
            method="DELETE",
            exceptions_for_status={404: ExperimentNotFound(self._not_found_err_msg(experiment_id))},
        )

    def list(self, workspace: Optional[str] = None) -> List[Experiment]:
        """
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises WorkspaceNotFound: If the workspace doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        workspace_name = self._resolve_workspace(workspace, ensure_exists=False)
        return [
            Experiment.from_json(d)
            for d in self.request(
                f"workspaces/{self._url_quote(workspace_name)}/experiments",
                exceptions_for_status={404: WorkspaceNotFound(workspace_name)},
            ).json()["data"]
        ]

    def logs(
        self,
        experiment: Union[str, Experiment],
        job_id: Optional[str] = None,
        quiet: bool = False,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for an experiment.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        :param experiment: The experiment ID, full name, or object.
        :param job_id: The ID of a specific job from the Beaker experiment to get the logs for.
            Required if there are more than one jobs in the experiment.
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        exp = self.get(experiment if isinstance(experiment, str) else experiment.id)
        if job_id is None:
            if len(exp.jobs) > 1:
                raise ValueError(
                    f"Experiment {exp.id} has more than 1 job. You need to specify the 'job_id'."
                )
            job_id = exp.jobs[0].id
        return self.beaker.job.logs(job_id, quiet=quiet)

    def await_all(
        self,
        experiment: Union[str, Experiment],
        timeout: Optional[int] = None,
        poll_interval: float = 2.0,
        quiet: bool = False,
    ) -> Experiment:
        """
        Wait for all jobs in an experiment to complete.

        :param experiment: The experiment ID, full name, or object.
        :param timeout: Maximum amount of time to wait for (in seocnds).
        :param poll_interval: Time to wait between polling the experiment (in seconds).
        :param quiet: If ``True``, progress won't be displayed.

        :raises ExperimentNotFound: If the experiment can't be found.
        :raises TimeoutError: If the ``timeout`` expires.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        start = time.time()
        with Progress(
            "[progress.description]{task.description}",
            SpinnerColumn(),
            TimeElapsedColumn(),
            disable=quiet,
        ) as progress:
            task_id = progress.add_task(f"Waiting on {experiment}:")
            polls = 0
            while True:
                exp = self.get(experiment if isinstance(experiment, str) else experiment.id)
                if exp.executions:
                    for execution in exp.executions:
                        if execution.state.exit_code is None:
                            break
                    else:
                        return exp
                if timeout is not None and time.time() - start >= timeout:
                    raise TimeoutError
                polls += 1
                progress.update(task_id, total=polls + 1, advance=1)
                time.sleep(poll_interval)

    def _not_found_err_msg(self, experiment: str) -> str:
        return (
            f"'{experiment}': Make sure you're using a valid Beaker experiment ID or the "
            f"*full* name of the experiment (with the account prefix, e.g. 'username/experiment_name')"
        )
