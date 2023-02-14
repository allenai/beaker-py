import io
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Union,
)

from ..aliases import PathOrStr
from ..data_model import *
from ..exceptions import *
from ..util import log_and_wait, path_is_relative_to, retriable
from .service_client import ServiceClient

if TYPE_CHECKING:
    from requests import Response
    from rich.progress import Progress, TaskID


is_canceled = None


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

    REQUEST_SIZE_LIMIT: ClassVar[int] = 32 * 1024 * 1024

    DOWNLOAD_CHUNK_SIZE: ClassVar[int] = 10 * 1024
    """
    The default buffer size for downloads.
    """

    def get(self, dataset: str) -> Dataset:
        """
        Get info about a dataset.

        :param dataset: The dataset ID or name.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

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
                # Try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{dataset}")
                except DatasetNotFound:
                    pass

                # Try searching the default workspace.
                if self.config.default_workspace is not None:
                    matches = self.beaker.workspace.datasets(match=dataset, limit=1)
                    if matches:
                        return matches[0]
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
                    data=DatasetSpec(workspace=workspace_id, description=description),
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset_id = self.resolve_dataset(dataset).id

        @retriable()
        def commit() -> Dataset:
            # It's okay to retry this because committing a dataset multiple
            # times does nothing.
            return Dataset.from_json(
                self.request(
                    f"datasets/{self.url_quote(dataset_id)}",
                    method="PATCH",
                    data=DatasetPatch(commit=True),
                    exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset))},
                ).json()
            )

        return commit()

    def fetch(
        self,
        dataset: Union[str, Dataset],
        target: Optional[PathOrStr] = None,
        force: bool = False,
        max_workers: Optional[int] = None,
        quiet: bool = False,
        validate_checksum: bool = True,
        chunk_size: Optional[int] = None,
        multiprocessing: bool = False,
    ):
        """
        Download a dataset.

        .. note::
            This method uses a :class:`~concurrent.futures.ThreadPoolExecutor` by default to
            download files concurrently. This is much faster than downloading files sequentially,
            however you may find that it's still pretty slow compared to the Beaker CLI when
            the dataset has many files. Unfortunately this is an inherent limitation of Python's GIL.

            To get around this you could try setting `multiprocessing=True`, which will
            force using a :class:`~concurrent.futures.ProcessPoolExecutor` instead.

        :param dataset: The dataset ID, name, or object.
        :param target: The target path to fetched data. Defaults to ``Path(.)``.
        :param max_workers: The maximum number of thread pool workers to use to download files concurrently.
        :param force: If ``True``, existing local files will be overwritten.
        :param quiet: If ``True``, progress won't be displayed.
        :param validate_checksum: If ``True``, the checksum of every file downloaded will be verified.
        :param chunk_size: The size of the buffer (in bytes) to use while downloading each file.
            Defaults to :data:`DOWNLOAD_CHUNK_SIZE`.
        :param multiprocessing: Use multiprocessing instead of threading.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileExistsError: If ``force=False`` and an existing local file clashes with a file
            in the Beaker dataset.
        :raises ChecksumFailedError: If ``validate_checksum=True`` and the digest of one of the
            downloaded files doesn't match the expected digest.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset)
        if dataset.storage is None:
            # Might need to get dataset again if 'storage' hasn't been set yet.
            dataset = self.get(dataset.id)
        if dataset.storage is None:
            raise DatasetReadError(dataset.id)

        dataset_info = DatasetInfo.from_json(
            self.request(
                f"datasets/{dataset.id}/files",
                exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset.id))},
            ).json()
        )
        total_bytes_to_download: int = dataset_info.size.bytes
        total_downloaded: int = 0

        target = Path(target or Path("."))
        target.mkdir(exist_ok=True, parents=True)

        from ..progress import get_sized_dataset_fetch_progress

        progress = get_sized_dataset_fetch_progress(quiet)

        with progress:
            bytes_task = progress.add_task("Downloading dataset")
            progress.update(bytes_task, total=total_bytes_to_download)

            import concurrent.futures
            import multiprocessing as mp
            import threading

            pool_type = (
                concurrent.futures.ProcessPoolExecutor
                if multiprocessing
                else concurrent.futures.ThreadPoolExecutor
            )
            with pool_type(max_workers=max_workers) as executor:
                global is_canceled
                is_canceled = mp.Event() if multiprocessing else threading.Event()
                download_futures = []
                try:
                    for file_info in dataset_info.page.data:
                        target_path = target / Path(file_info.path)
                        if not force and target_path.exists():
                            raise FileExistsError(file_info.path)
                        future = executor.submit(
                            self._download_file,
                            dataset,
                            file_info,
                            target_path,
                            progress=progress if not multiprocessing else None,
                            task_id=bytes_task if not multiprocessing else None,
                            validate_checksum=validate_checksum,
                            chunk_size=chunk_size,
                        )
                        download_futures.append(future)

                    for future in concurrent.futures.as_completed(download_futures):
                        total_downloaded += future.result()
                        progress.update(bytes_task, completed=total_downloaded)
                except KeyboardInterrupt:
                    self.logger.warning("Received KeyboardInterrupt, canceling download workers...")
                    is_canceled.set()  # type: ignore
                    for future in download_futures:
                        future.cancel()
                    executor.shutdown(wait=True)
                    raise

            progress.update(bytes_task, total=total_downloaded, completed=total_downloaded)

    def stream_file(
        self,
        dataset: Union[str, Dataset],
        file: Union[str, FileInfo],
        offset: int = 0,
        length: int = -1,
        quiet: bool = False,
        validate_checksum: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Generator[bytes, None, None]:
        """
        Stream download the contents of a single file from a dataset.

        .. seealso::
            :meth:`get_file()` is similar but returns the entire contents at once instead of
            a generator over the contents.

        :param dataset: The dataset ID, name, or object.
        :param file: The path of the file within the dataset or the corresponding
            :class:`~beaker.data_model.dataset.FileInfo` object.
        :param offset: Offset to start from, in bytes.
        :param length: Number of bytes to read.
        :param quiet: If ``True``, progress won't be displayed.
        :param validate_checksum: If ``True``, the checksum of the downloaded bytes will be verified.
        :param chunk_size: The size of the buffer (in bytes) to use while downloading each file.
            Defaults to :data:`DOWNLOAD_CHUNK_SIZE`.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileNotFoundError: If the file doesn't exist in the dataset.
        :raises ChecksumFailedError: If ``validate_checksum=True`` and the digest of the downloaded
            bytes don't match the expected digest.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

        :examples:

        >>> total_bytes = 0
        >>> with open(tmp_path / "squad-train.arrow", "wb") as f:
        ...     for chunk in beaker.dataset.stream_file(squad_dataset_name, "squad-train.arrow", quiet=True):
        ...         total_bytes += f.write(chunk)
        """
        dataset = self.resolve_dataset(dataset, ensure_storage=True)
        file_info = file if isinstance(file, FileInfo) else self.file_info(dataset, file)

        from ..progress import get_unsized_dataset_fetch_progress

        with get_unsized_dataset_fetch_progress(quiet=quiet) as progress:
            task_id = progress.add_task("Downloading", total=None)
            for bytes_chunk in self._stream_file(
                dataset,
                file_info,
                offset=offset,
                length=length,
                validate_checksum=validate_checksum,
                chunk_size=chunk_size,
            ):
                progress.update(task_id, advance=len(bytes_chunk))
                yield bytes_chunk

    def get_file(
        self,
        dataset: Union[str, Dataset],
        file: Union[str, FileInfo],
        offset: int = 0,
        length: int = -1,
        quiet: bool = False,
        validate_checksum: bool = True,
        chunk_size: Optional[int] = None,
    ) -> bytes:
        """
        Download the contents of a single file from a dataset.

        .. seealso::
            :meth:`stream_file()` is similar but returns a generator over the contents.

        :param dataset: The dataset ID, name, or object.
        :param file: The path of the file within the dataset or the corresponding
            :class:`~beaker.data_model.dataset.FileInfo` object.
        :param offset: Offset to start from, in bytes.
        :param length: Number of bytes to read.
        :param quiet: If ``True``, progress won't be displayed.
        :param validate_checksum: If ``True``, the checksum of the downloaded bytes will be verified.
        :param chunk_size: The size of the buffer (in bytes) to use while downloading each file.
            Defaults to :data:`DOWNLOAD_CHUNK_SIZE`.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileNotFoundError: If the file doesn't exist in the dataset.
        :raises ChecksumFailedError: If ``validate_checksum=True`` and the digest of the downloaded
            bytes don't match the expected digest.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

        :examples:

        >>> contents = beaker.dataset.get_file(squad_dataset_name, "squad-train.arrow", quiet=True)
        """

        @retriable(recoverable_errors=(RequestException, ChecksumFailedError))
        def _get_file() -> bytes:
            return b"".join(
                self.stream_file(
                    dataset,
                    file,
                    offset=offset,
                    length=length,
                    quiet=quiet,
                    validate_checksum=validate_checksum,
                    chunk_size=chunk_size,
                )
            )

        return _get_file()

    def file_info(self, dataset: Union[str, Dataset], file_name: str) -> FileInfo:
        """
        Get the :class:`~beaker.data_model.dataset.FileInfo` for a file in a dataset.

        :param dataset: The dataset ID, name, or object.
        :param file_name: The path of the file within the dataset.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises FileNotFoundError: If the file doesn't exist in the dataset.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset, ensure_storage=True)
        assert dataset.storage is not None
        if dataset.storage.scheme == "fh":
            response = self.request(
                f"datasets/{dataset.storage.id}/files/{file_name}",
                method="HEAD",
                token=dataset.storage.token,
                base_url=dataset.storage.base_url,
                exceptions_for_status={404: FileNotFoundError(file_name)},
            )
            size_str = response.headers.get(self.HEADER_CONTENT_LENGTH)
            size = int(size_str) if size_str else None
            return FileInfo(
                path=file_name,
                digest=Digest.from_encoded(response.headers[self.HEADER_DIGEST]),
                updated=datetime.strptime(
                    response.headers[self.HEADER_LAST_MODIFIED], "%a, %d %b %Y %H:%M:%S %Z"
                ),
                size=size,
            )
        else:
            # TODO (epwalsh): make a HEAD request once Beaker supports that
            # (https://github.com/allenai/beaker/issues/2961)
            response = self.request(
                f"datasets/{dataset.id}/files/{urllib.parse.quote(file_name, safe='')}",
                stream=True,
                exceptions_for_status={404: FileNotFoundError(file_name)},
            )
            response.close()
            size_str = response.headers.get(self.HEADER_CONTENT_LENGTH)
            size = int(size_str) if size_str else None
            digest = response.headers.get(self.HEADER_DIGEST)
            return FileInfo(
                path=file_name,
                digest=None if digest is None else Digest.from_encoded(digest),
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset)
        if dataset.committed is not None:
            raise DatasetWriteError(dataset.id)

        from ..progress import get_dataset_sync_progress

        with get_dataset_sync_progress(quiet) as progress:
            bytes_task = progress.add_task("Uploading dataset")
            total_bytes = 0
            # map source path to (target_path, size)
            path_info: Dict[Path, Tuple[Path, int]] = {}
            for source in sources:
                source = Path(source)
                strip_path = strip_paths or not path_is_relative_to(source, ".")
                if source.is_file():
                    target_path = Path(source.name) if strip_path else source
                    if target is not None:
                        target_path = Path(str(target)) / target_path
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
                            target_path = Path(str(target)) / target_path
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
                        ignore_errors=True,
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

    def upload(
        self,
        dataset: Union[str, Dataset],
        source: bytes,
        target: PathOrStr,
        quiet: bool = False,
    ) -> None:
        """
        Upload raw bytes to an uncommitted dataset.

        :param dataset: The dataset ID, name, or object.
        :param source: The raw bytes to upload to the dataset.
        :param target: The name to assign to the file for the bytes in the dataset.
        :param quiet: If ``True``, progress won't be displayed.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetWriteError: If the dataset was already committed.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset)
        if dataset.committed is not None:
            raise DatasetWriteError(dataset.id)

        from ..progress import get_dataset_sync_progress

        size = len(source)
        with get_dataset_sync_progress(quiet) as progress:
            task_id = progress.add_task("Uploading source")
            if size is not None:
                progress.update(task_id, total=size)
            self._upload_file(dataset, size, source, target, progress, task_id)

    def ls(self, dataset: Union[str, Dataset], prefix: Optional[str] = None) -> List[FileInfo]:
        """
        List files in a dataset.

        :param dataset: The dataset ID, name, or object.
        :param prefix: An optional path prefix to filter by.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetReadError: If the :data:`~beaker.data_model.dataset.Dataset.storage` hasn't been set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset)
        query = {} if prefix is None else {"prefix": prefix}
        info = DatasetInfo.from_json(
            self.request(
                f"datasets/{dataset.id}/files",
                query=query,
                exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset.id))},
            ).json()
        )
        return list(info.page.data)

    def size(self, dataset: Union[str, Dataset]) -> int:
        """
        Calculate the size of a dataset, in bytes.

        :param dataset: The dataset ID, name, or object.

        :raises DatasetNotFound: If the dataset can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        dataset = self.resolve_dataset(dataset)
        info = DatasetInfo.from_json(
            self.request(
                f"datasets/{dataset.id}/files",
                exceptions_for_status={404: DatasetNotFound(self._not_found_err_msg(dataset.id))},
            ).json()
        )
        return info.size.bytes

    def rename(self, dataset: Union[str, Dataset], name: str) -> Dataset:
        """
        Rename a dataset.

        :param dataset: The dataset ID, name, or object.
        :param name: The new name of the dataset.

        :raises ValueError: If the new name is invalid.
        :raises DatasetNotFound: If the dataset can't be found.
        :raises DatasetConflict: If a dataset by that name already exists.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        return f"{self.config.agent_address}/ds/{self.url_quote(dataset_id)}"

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
        source: Union[PathOrStr, bytes],
        target: PathOrStr,
        progress: "Progress",
        task_id: "TaskID",
        ignore_errors: bool = False,
    ) -> int:
        from ..progress import BufferedReaderWithProgress

        assert dataset.storage is not None
        if dataset.storage.scheme != "fh":
            raise NotImplementedError(
                f"Datasets API is not implemented for '{dataset.storage.scheme}' backend yet"
            )

        source_file_wrapper: BufferedReaderWithProgress
        if isinstance(source, (str, Path, os.PathLike)):
            source = Path(source)
            if ignore_errors and not source.exists():
                return 0
            source_file_wrapper = BufferedReaderWithProgress(source.open("rb"), progress, task_id)
        elif isinstance(source, bytes):
            source_file_wrapper = BufferedReaderWithProgress(io.BytesIO(source), progress, task_id)
        else:
            raise ValueError(f"Expected path-like or raw bytes, got {type(source)}")

        try:
            body: Optional[BufferedReaderWithProgress] = source_file_wrapper
            digest: Optional[str] = None

            if size > self.REQUEST_SIZE_LIMIT:

                @retriable()
                def get_upload_id() -> str:
                    assert dataset.storage is not None  # for mypy
                    response = self.request(
                        "uploads",
                        method="POST",
                        token=dataset.storage.token,
                        base_url=dataset.storage.base_url,
                    )
                    return response.headers[self.HEADER_UPLOAD_ID]

                upload_id = get_upload_id()

                written = 0
                while written < size:
                    chunk = source_file_wrapper.read(self.REQUEST_SIZE_LIMIT)
                    if not chunk:
                        break

                    @retriable()
                    def upload() -> "Response":
                        assert dataset.storage is not None  # for mypy
                        return self.request(
                            f"uploads/{upload_id}",
                            method="PATCH",
                            data=chunk,
                            token=dataset.storage.token,
                            base_url=dataset.storage.base_url,
                            headers={
                                self.HEADER_UPLOAD_LENGTH: str(size),
                                self.HEADER_UPLOAD_OFFSET: str(written),
                            },
                        )

                    response = upload()
                    written += len(chunk)

                    digest = response.headers.get(self.HEADER_DIGEST)
                    if digest:
                        break

                if written != size:
                    raise UnexpectedEOFError(str(source))

                body = None

            @retriable()
            def finalize():
                assert dataset.storage is not None  # for mypy
                self.request(
                    f"datasets/{dataset.storage.id}/files/{str(target)}",
                    method="PUT",
                    data=body,
                    token=dataset.storage.token,
                    base_url=dataset.storage.base_url,
                    headers=None if not digest else {self.HEADER_DIGEST: digest},
                    stream=body is not None,
                    exceptions_for_status={
                        403: DatasetWriteError(dataset.id),
                        404: DatasetNotFound(self._not_found_err_msg(dataset.id)),
                    },
                )

            finalize()

            return source_file_wrapper.total_read
        finally:
            source_file_wrapper.close()

    def _stream_file(
        self,
        dataset: Dataset,
        file: FileInfo,
        chunk_size: Optional[int] = None,
        offset: int = 0,
        length: int = -1,
        validate_checksum: bool = True,
    ) -> Generator[bytes, None, None]:
        def stream_file() -> Generator[bytes, None, None]:
            headers = {}
            if offset > 0 and length > 0:
                headers["Range"] = f"bytes={offset}-{offset + length - 1}"
            elif offset > 0:
                headers["Range"] = f"bytes={offset}-"
            response = self.request(
                f"datasets/{dataset.id}/files/{urllib.parse.quote(file.path, safe='')}",
                method="GET",
                stream=True,
                headers=headers,
                exceptions_for_status={404: FileNotFoundError(file.path)},
            )
            for chunk in response.iter_content(chunk_size=chunk_size or self.DOWNLOAD_CHUNK_SIZE):
                yield chunk

        if is_canceled is not None and is_canceled.is_set():  # type: ignore
            raise ThreadCanceledError

        contents_hash = None
        if offset == 0 and validate_checksum and file.digest is not None:
            contents_hash = file.digest.new_hasher()

        retries = 0
        while True:
            try:
                for chunk in stream_file():
                    if is_canceled is not None and is_canceled.is_set():  # type: ignore
                        raise ThreadCanceledError
                    offset += len(chunk)
                    if contents_hash is not None:
                        contents_hash.update(chunk)
                    yield chunk
                break
            except RequestException as err:
                if retries < self.beaker.MAX_RETRIES:
                    log_and_wait(retries, err)
                    retries += 1
                else:
                    raise

        # Validate digest.
        if file.digest is not None and contents_hash is not None:
            actual_digest = Digest.from_decoded(
                contents_hash.digest(), algorithm=file.digest.algorithm
            )
            if actual_digest != file.digest:
                raise ChecksumFailedError(
                    f"Checksum for '{file.path}' failed. "
                    f"Expected '{file.digest}', got '{actual_digest}'."
                )

    def _download_file(
        self,
        dataset: Dataset,
        file: FileInfo,
        target_path: Path,
        progress: Optional["Progress"] = None,
        task_id: Optional["TaskID"] = None,
        validate_checksum: bool = True,
        chunk_size: Optional[int] = None,
    ) -> int:
        import tempfile

        total_bytes = 0
        target_dir = target_path.parent
        target_dir.mkdir(exist_ok=True, parents=True)

        def on_failure():
            if progress is not None and task_id is not None:
                progress.advance(task_id, -total_bytes)

        @retriable(
            on_failure=on_failure,
            recoverable_errors=(RequestException, ChecksumFailedError),
        )
        def download() -> int:
            nonlocal total_bytes

            tmp_target = tempfile.NamedTemporaryFile(
                "w+b", dir=target_dir, delete=False, suffix=".tmp"
            )
            try:
                for chunk in self._stream_file(
                    dataset,
                    file,
                    validate_checksum=validate_checksum,
                    chunk_size=chunk_size,
                ):
                    total_bytes += len(chunk)
                    tmp_target.write(chunk)
                    if progress is not None and task_id is not None:
                        progress.update(task_id, advance=len(chunk))
                os.replace(tmp_target.name, target_path)
            finally:
                tmp_target.close()
                if os.path.exists(tmp_target.name):
                    os.remove(tmp_target.name)
            return total_bytes

        return download()
