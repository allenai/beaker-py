import os
from pathlib import Path
from typing import Deque, Dict, Generator, List, Optional, Union

from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from ..util import BufferedReaderWithProgress, DownloadUploadColumn
from .service_client import ServiceClient


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
        commit: bool = True,
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
        :param commit: Whether to commit the dataset after successful upload.

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
        if commit:
            self.commit(dataset_info.id)

        # Return info about the dataset.
        return self.get(dataset_info.id)

    def commit(self, dataset: Union[str, Dataset]):
        """
        Commit the dataset.

        :param dataset: The dataset ID, full name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset_id = dataset if isinstance(dataset, str) else dataset.id
        self.request(
            f"datasets/{self._url_quote(dataset_id)}",
            method="PATCH",
            data={"commit": True},
        )

    def fetch(
        self,
        dataset: Union[str, Dataset],
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
        dataset: Dataset = self.get(dataset.id if isinstance(dataset, Dataset) else dataset)
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
                f"datasets/{self._url_quote(dataset)}",
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
