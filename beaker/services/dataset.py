import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Deque, Dict, Generator, Optional, Tuple, Union

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from ..util import path_is_relative_to
from .service_client import ServiceClient

if TYPE_CHECKING:
    from rich.progress import Progress, TaskID


class DatasetClient(ServiceClient):
    """
    Accessed via :data:`Beaker.dataset <beaker.Beaker.dataset>`.
    """

    HEADER_UPLOAD_ID = "Upload-ID"
    HEADER_UPLOAD_LENGTH = "Upload-Length"
    HEADER_UPLOAD_OFFSET = "Upload-Offset"
    HEADER_DIGEST = "Digest"
    HEADER_LAST_MODIFIED = "Last-Modified"
    HEADER_CONTENT_LENGTH = "Content-Length"

    REQUEST_SIZE_LIMIT = 32 * 1024 * 1024

    def get(self, dataset: str) -> Dataset:
        """
        Get info about a dataset.

        :param dataset: The dataset ID or name.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """

        def _get(id: str) -> Dataset:
            return Dataset.from_json(
                self.request(
                    f"datasets/{self.url_quote(id)}",
                    exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be a dataset ID or full name, so we try that first.
            return _get(dataset)
        except DatasetNotFound:
            if "/" not in dataset:
                # Now try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{dataset}")
                except DatasetNotFound:
                    pass
            raise

    def create(
        self,
        name: str,
        *sources: PathOrStr,
        target: Optional[PathOrStr] = None,
        workspace: Optional[str] = None,
        description: Optional[str] = None,
        force: bool = False,
        max_workers: Optional[int] = None,
        quiet: bool = False,
        commit: bool = True,
        strip_paths: bool = False,
    ) -> Dataset:
        """
        Create a dataset with the source file(s).

        :param name: The name to assign to the new dataset.
        :param sources: Local source files or directories to upload to the dataset.
        :param target: If specified, all source files/directories will be uploaded under
            a directory of this name.
        :param workspace: The workspace to upload the dataset to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param description: Text description for the dataset.
        :param force: If ``True`` and a dataset by the given name already exists, it will be overwritten.
        :param max_workers: The maximum number of thread pool workers to use to upload files concurrently.
        :param quiet: If ``True``, progress won't be displayed.
        :param commit: Whether to commit the dataset after successful upload.
        :param strip_paths: If ``True``, all source files and directories will be uploaded under their name,
            not their path. E.g. the file "docs/source/index.rst" would be uploaded as just "index.rst",
            instead of "docs/source/index.rst".

            .. note::
                This only applies to source paths that are children of the current working directory.
                If a source path is outside of the current working directory, it will always
                be uploaded under its name only.

        :raises ValueError: If the name is invalid.
        :raises DatasetConflict: If a dataset by that name already exists and ``force=False``.
        :raises UnexpectedEOFError: If a source file is an empty file, or if a source is a directory and
            the contents of one of the directory's files changes while creating the dataset.
        :raises FileNotFoundError: If a source doesn't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        workspace_id = self.resolve_workspace(workspace).id

        # Create the dataset.
        def make_dataset() -> Dataset:
            return Dataset.from_json(
                self.request(
                    "datasets",
                    method="POST",
                    query={"name": name},
                    data=DatasetSpec(
                        workspace=workspace_id, description=description, fileheap=True
                    ),
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
        if sources:
            self.sync(
                dataset_info,
                *sources,
                target=target,
                quiet=quiet,
                max_workers=max_workers,
                strip_paths=strip_paths,
            )

        # Commit the dataset.
        if commit:
            self.commit(dataset_info.id)

        # Return info about the dataset.
        return self.get(dataset_info.id)

    def commit(self, dataset: Union[str, Dataset]) -> Dataset:
        """
        Commit the dataset.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset_id = self.resolve_dataset(dataset).id
        return Dataset.from_json(
            self.request(
                f"datasets/{self.url_quote(dataset_id)}",
                method="PATCH",
                data=DatasetPatch(commit=True),
                exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset))},
            ).json()
        )

    def fetch(
        self,
        dataset: Union[str, Dataset],
        target: Optional[PathOrStr] = None,
        force: bool = False,
        max_workers: Optional[int] = None,
        quiet: bool = False,
        validate_checksum: bool = True,
    ):
        """
        Download a dataset.

        :param dataset: The dataset ID, name, or object.
        :param target: The target path to fetched data. Defaults to ``Path(.)``.
        :param max_workers: The maximum number of thread pool workers to use to download files concurrently.
        :param force: If ``True``, existing local files will be overwritten.
        :param quiet: If ``True``, progress won't be displayed.
        :param validate_checksum: If ``True``, the checksum of every file downloaded will be verified.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileExistsError: If ``force=False`` and an existing local file clashes with a file
            in the Beaker dataset.
        :raises ChecksumFailedError: If ``validate_checksum=True`` and the digest of one of the
            downloaded files doesn't match the expected digest.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.resolve_dataset(dataset)
        if dataset.storage is None:
            # Might need to get dataset again if 'storage' hasn't been set yet.
            dataset = self.get(dataset.id)
        if dataset.storage is None:
            raise DatasetReadError(dataset.id)

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
        from ..progress import (
            get_sized_dataset_fetch_progress,
            get_unsized_dataset_fetch_progress,
        )

        if storage_info.size is not None and storage_info.size.final:
            total_bytes_to_download = storage_info.size.bytes
            progress = get_sized_dataset_fetch_progress(quiet)
        else:
            progress = get_unsized_dataset_fetch_progress(quiet)

        with progress:
            bytes_task = progress.add_task("Downloading dataset")
            if total_bytes_to_download is not None:
                progress.update(bytes_task, total=total_bytes_to_download)

            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                download_futures = []
                for file_info in self._iter_files(dataset.storage):
                    assert file_info.size is not None
                    if total_bytes_to_download is None:
                        progress.update(bytes_task, total=total_downloaded + file_info.size + 1)
                    target_path = target / Path(file_info.path)
                    if not force and target_path.exists():
                        raise FileExistsError(file_info.path)
                    future = executor.submit(
                        self._download_file,
                        dataset.storage,
                        file_info,
                        target_path,
                        progress,
                        bytes_task,
                        validate_checksum,
                    )
                    download_futures.append(future)

                for future in concurrent.futures.as_completed(download_futures):
                    total_downloaded += future.result()

            if total_bytes_to_download is None:
                progress.update(bytes_task, total=total_downloaded, completed=total_downloaded)

    def stream_file(
        self,
        dataset: Union[str, Dataset],
        file: Union[str, FileInfo],
        offset: int = 0,
        length: int = -1,
        max_retries: int = 5,
        quiet: bool = False,
        validate_checksum: bool = True,
    ) -> Generator[bytes, None, None]:
        """
        Stream download the contents of a single file from a dataset.

        :param dataset: The dataset ID, name, or object.
        :param file: The path of the file within the dataset or the corresponding
            :class:`~beaker.data_model.dataset.FileInfo` object.
        :param offset: Offset to start from, in bytes.
        :param length: Number of bytes to read.
        :param max_retries: Number of times to restart the download when HTTP errors occur.
            Errors can be expected for very large files.
        :param quiet: If ``True``, progress won't be displayed.
        :param validate_checksum: If ``True``, the checksum of the downloaded bytes will be verified.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileNotFoundError: If the file doesn't exist in the dataset.
        :raises ChecksumFailedError: If ``validate_checksum=True`` and the digest of the downloaded
            bytes don't match the expected digest.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.resolve_dataset(dataset, ensure_storage=True)
        assert dataset.storage is not None

        file_info = file if isinstance(file, FileInfo) else self.file_info(dataset, file)

        from ..progress import get_unsized_dataset_fetch_progress

        with get_unsized_dataset_fetch_progress(quiet=quiet) as progress:
            task_id = progress.add_task("Downloading", total=None)
            for bytes_chunk in self._stream_file(
                dataset.storage,
                file_info,
                offset=offset,
                length=length,
                max_retries=max_retries,
                validate_checksum=validate_checksum,
            ):
                progress.update(task_id, advance=len(bytes_chunk))
                yield bytes_chunk

    def file_info(self, dataset: Union[str, Dataset], file_name: str) -> FileInfo:
        """
        Get the :class:`~beaker.data_model.dataset.FileInfo` for a file in a dataset.

        :param dataset: The dataset ID, name, or object.
        :param file_name: The path of the file within the dataset.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileNotFoundError: If the file doesn't exist in the dataset.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.resolve_dataset(dataset, ensure_storage=True)
        assert dataset.storage is not None
        response = self.request(
            f"datasets/{dataset.storage.id}/files/{file_name}",
            method="HEAD",
            token=dataset.storage.token,
            base_url=dataset.storage.address,
            exceptions_for_status={404: FileNotFoundError(file_name)},
        )
        size_str = response.headers.get(self.HEADER_CONTENT_LENGTH)
        size = int(size_str) if size_str else None
        return FileInfo(
            path=file_name,
            digest=response.headers[self.HEADER_DIGEST],
            updated=datetime.strptime(
                response.headers[self.HEADER_LAST_MODIFIED], "%a, %d %b %Y %H:%M:%S %Z"
            ),
            size=size,
        )

    def delete(self, dataset: Union[str, Dataset]):
        """
        Delete a dataset.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset_id = self.resolve_dataset(dataset).id
        self.request(
            f"datasets/{self.url_quote(dataset_id)}",
            method="DELETE",
            exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset))},
        )

    def sync(
        self,
        dataset: Union[str, Dataset],
        *sources: PathOrStr,
        target: Optional[PathOrStr] = None,
        quiet: bool = False,
        max_workers: Optional[int] = None,
        strip_paths: bool = False,
    ) -> None:
        """
        Sync local files or directories to an uncommitted dataset.

        :param dataset: The dataset ID, name, or object.
        :param sources: Local source files or directories to upload to the dataset.
        :param target: If specified, all source files/directories will be uploaded under
            a directory of this name.
        :param max_workers: The maximum number of thread pool workers to use to upload files concurrently.
        :param quiet: If ``True``, progress won't be displayed.
        :param strip_paths: If ``True``, all source files and directories will be uploaded under their name,
            not their path. E.g. the file "docs/source/index.rst" would be uploaded as just "index.rst",
            instead of "docs/source/index.rst".

            .. note::
                This only applies to source paths that are children of the current working directory.
                If a source path is outside of the current working directory, it will always
                be uploaded under its name only.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetWriteError: If the dataset was already committed.
        :raises FileNotFoundError: If a source doesn't exist.
        :raises UnexpectedEOFError: If a source is an empty file, or if a source is a directory and
            the contents of one of the directory's files changes while creating the dataset.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.resolve_dataset(dataset)
        if dataset.committed is not None:
            raise DatasetWriteError(dataset.id)

        from ..progress import get_dataset_sync_progress

        with get_dataset_sync_progress(quiet) as progress:
            bytes_task = progress.add_task("Uploading dataset")
            total_bytes = 0
            # map source path to (target_path, size)
            path_info: Dict[Path, Tuple[Path, int]] = {}
            for name in sources:
                source = Path(name)
                strip_path = strip_paths or not path_is_relative_to(source, ".")
                if source.is_file():
                    target_path = Path(source.name) if strip_path else source
                    if target is not None:
                        target_path = Path(target) / target_path
                    size = source.lstat().st_size
                    if size == 0:
                        raise UnexpectedEOFError(f"'{source}', empty files are not allowed")
                    path_info[source] = (target_path, size)
                    total_bytes += size
                elif source.is_dir():
                    for path in source.glob("**/*"):
                        if path.is_dir():
                            continue
                        target_path = path.relative_to(source) if strip_path else path
                        if target is not None:
                            target_path = Path(target) / target_path
                        size = path.lstat().st_size
                        if size == 0:
                            continue
                        path_info[path] = (target_path, size)
                        total_bytes += size
                else:
                    raise FileNotFoundError(source)

            import concurrent.futures

            progress.update(bytes_task, total=total_bytes)

            # Now upload.
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Dispatch tasks to thread pool executor.
                future_to_path = {}
                for path, (target_path, size) in path_info.items():
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
                    original_size = path_info[path][1]
                    actual_size = future.result()
                    if actual_size != original_size:
                        # If the size of the file has changed since we started, adjust total.
                        total_bytes += actual_size - original_size
                        progress.update(bytes_task, total=total_bytes)

    def ls(self, dataset: Union[str, Dataset]) -> Generator[FileInfo, None, None]:
        """
        List files in a dataset.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        dataset: Dataset = self.resolve_dataset(dataset)
        if dataset.storage is None:
            # Might need to get dataset again if 'storage' hasn't been set yet.
            dataset = self.get(dataset.id)
        if dataset.storage is None:
            raise DatasetReadError(dataset.id)
        for file_info in self._iter_files(dataset.storage):
            yield file_info

    def size(self, dataset: Union[str, Dataset]) -> int:
        """
        Calculate the size of a dataset, in bytes.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        total = 0
        for file_info in self.ls(dataset):
            assert file_info.size is not None
            total += file_info.size
        return total

    def rename(self, dataset: Union[str, Dataset], name: str) -> Dataset:
        """
        Rename a dataset.

        :param dataset: The dataset ID, name, or object.
        :param name: The new name of the dataset.

        :raises ValueError: If the new name is invalid.
        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetConflict: If a dataset by that name already exists.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        dataset_id = self.resolve_dataset(dataset).id
        return Dataset.from_json(
            self.request(
                f"datasets/{self.url_quote(dataset_id)}",
                method="PATCH",
                data=DatasetPatch(name=name),
                exceptions_for_status={
                    409: DatasetConflict(name),
                    404: DatasetNotFound(dataset_id),
                },
            ).json()
        )

    def url(self, dataset: Union[str, Dataset]) -> str:
        """
        Get the URL for a dataset.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        """
        dataset_id = self.resolve_dataset(dataset).id
        return f"{self.config.agent_address}/ds/{self.url_quote(dataset_id)}/details"

    def _not_found_err_msg(self, dataset: Union[str, Dataset]) -> str:
        dataset = dataset if isinstance(dataset, str) else dataset.id
        return (
            f"'{dataset}': Make sure you're using a valid Beaker dataset ID or the "
            f"*full* name of the dataset (with the account prefix, e.g. 'username/dataset_name')"
        )

    def _upload_file(
        self,
        dataset: Dataset,
        size: int,
        source: PathOrStr,
        target: PathOrStr,
        progress: "Progress",
        task_id: "TaskID",
        ignore_errors: bool = False,
    ) -> int:
        source: Path = Path(source)
        assert dataset.storage is not None
        if ignore_errors and not source.exists():
            return 0

        with source.open("rb") as source_file:
            from ..progress import BufferedReaderWithProgress

            source_file_wrapper = BufferedReaderWithProgress(source_file, progress, task_id)
            body: Optional[BufferedReaderWithProgress] = source_file_wrapper
            digest: Optional[str] = None

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

                    digest = response.headers.get(self.HEADER_DIGEST)
                    if digest:
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
                headers=None if not digest else {self.HEADER_DIGEST: digest},
                stream=body is not None,
                exceptions_for_status={
                    403: DatasetWriteError(dataset.id),
                    404: DatasetNotFound(self._not_found_err_msg(dataset.id)),
                },
            )

            return source_file_wrapper.total_read

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

    def _stream_file(
        self,
        storage: DatasetStorage,
        file_info: FileInfo,
        chunk_size: int = 1024,
        offset: int = 0,
        length: int = -1,
        max_retries: int = 5,
        validate_checksum: bool = True,
    ) -> Generator[bytes, None, None]:
        import hashlib

        def stream_file(offset: int, length: int) -> Generator[bytes, None, None]:
            headers = {}
            if offset > 0 and length > 0:
                headers["Range"] = f"bytes={offset}-{offset + length - 1}"
            elif offset > 0:
                headers["Range"] = f"bytes={offset}-"
            response = self.request(
                f"datasets/{storage.id}/files/{file_info.path}",
                method="GET",
                stream=True,
                headers=headers,
                token=storage.token,
                base_url=storage.address,
                exceptions_for_status={404: FileNotFoundError(file_info.path)},
            )
            for chunk in response.iter_content(chunk_size=chunk_size):
                yield chunk

        sha256_hash = hashlib.sha256() if (offset == 0 and validate_checksum) else None
        retries = 0
        while True:
            try:
                for chunk in stream_file(offset, length):
                    offset += len(chunk)
                    if sha256_hash is not None:
                        sha256_hash.update(chunk)
                    yield chunk
                break
            except HTTPError:
                if retries >= max_retries:
                    raise
                retries += 1

        # Validate digest.
        if sha256_hash is not None:
            digest = Digest(sha256_hash.digest())
            if file_info.digest != digest:
                raise ChecksumFailedError(
                    f"Checksum for '{file_info.path}' failed. "
                    f"Expected '{file_info.digest}', got '{digest}'."
                )

    def _download_file(
        self,
        storage: DatasetStorage,
        file_info: FileInfo,
        target_path: Path,
        progress: "Progress",
        task_id: "TaskID",
        validate_checksum: bool = True,
    ) -> int:
        import tempfile

        total_bytes = 0
        target_dir = target_path.parent
        target_dir.mkdir(exist_ok=True, parents=True)
        tmp_target = tempfile.NamedTemporaryFile("w+b", dir=target_dir, delete=False, suffix=".tmp")
        try:
            for chunk in self._stream_file(storage, file_info, validate_checksum=validate_checksum):
                total_bytes += len(chunk)
                tmp_target.write(chunk)
                progress.update(task_id, advance=len(chunk))
            os.replace(tmp_target.name, target_path)
        finally:
            tmp_target.close()
            if os.path.exists(tmp_target.name):
                os.remove(tmp_target.name)
        return total_bytes
