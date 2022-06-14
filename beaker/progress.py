import io
import time
from typing import List, Optional, Tuple

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskID,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text


class ImageDownloadUploadColumn(DownloadColumn):
    def render(self, task: Task) -> Text:
        if task.total is None or int(task.total) == 1:
            return Text("")
        else:
            return super().render(task)


class TaskStatusColumn(ProgressColumn):
    def __init__(self):
        super().__init__()
        self.dots = 0
        self.max_dots = 4
        self.update_interval = 1.0
        self.last_updated = time.time()

    def render(self, task: Task) -> Text:
        total = max(0, task.total or 0)
        completed = max(0, task.completed)
        if completed < total:
            now = time.time()
            if now - self.last_updated > self.update_interval:
                self.last_updated = now
                self.dots += 1
                if self.dots > self.max_dots:
                    self.dots = 0
            return Text("waiting" + ("." * self.dots) + (" " * (self.max_dots - self.dots)))
        else:
            return Text("\N{check mark} finalized")


class BufferedReaderWithProgress(io.BufferedReader):
    def __init__(self, handle: io.BufferedReader, progress: Progress, task_id: TaskID):
        super().__init__(handle.raw)
        self.handle = handle
        self.progress = progress
        self.task_id = task_id
        self.total_read = 0

    def __enter__(self) -> "BufferedReaderWithProgress":
        self.handle.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def closed(self) -> bool:
        return self.handle.closed

    def close(self):
        self.handle.close()

    def fileno(self):
        return self.handle.fileno()

    def flush(self):
        self.handle.flush()

    def isatty(self) -> bool:
        return self.handle.isatty()

    def readable(self) -> bool:
        return self.handle.readable()

    def seekable(self) -> bool:
        return self.handle.seekable()

    def writable(self) -> bool:
        return False

    def peek(self, size: int = 0) -> bytes:
        return self.handle.peek(size)

    def read(self, size: Optional[int] = None) -> bytes:
        out = self.handle.read(size)
        self.progress.advance(self.task_id, len(out))
        self.total_read += len(out)
        return out

    def read1(self, size: int = -1) -> bytes:
        out = self.handle.read1(size)
        self.progress.advance(self.task_id, len(out))
        self.total_read += len(out)
        return out

    def readinto(self, b):
        n = self.handle.readinto(b)
        self.progress.advance(self.task_id, n)
        self.total_read += n
        return n

    def readinto1(self, b):
        n = self.handle.readinto1(b)
        self.progress.advance(self.task_id, n)
        self.total_read += n
        return n

    def readline(self, size: Optional[int] = -1) -> bytes:
        out = self.handle.readline(size)
        self.progress.advance(self.task_id, len(out))
        self.total_read += len(out)
        return out

    def readlines(self, hint: int = -1) -> List[bytes]:
        lines = self.handle.readlines(hint)
        for line in lines:
            self.progress.advance(self.task_id, len(line))
            self.total_read += len(line)
        return lines

    def seek(self, offset: int, whence: int = 0) -> int:
        pos = self.handle.seek(offset, whence)
        self.progress.update(self.task_id, completed=pos)
        return pos

    def tell(self) -> int:
        return self.handle.tell()

    @property
    def raw(self):
        return self.handle.raw

    def detach(self):
        return self.handle.detach()

    def write(self, s) -> int:
        raise io.UnsupportedOperation("write")

    def writelines(self, lines):
        raise io.UnsupportedOperation("write")


def get_experiments_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        MofNCompleteColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        disable=quiet,
    )


def get_jobs_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        TaskStatusColumn(),
        TimeElapsedColumn(),
        disable=quiet,
    )


def get_logs_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        FileSizeColumn(),
        TimeElapsedColumn(),
        disable=quiet,
    )


def get_group_experiments_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        FileSizeColumn(),
        TimeElapsedColumn(),
        disable=quiet,
    )


def get_exps_and_jobs_progress(quiet: bool = False) -> Tuple[Live, Progress, Progress]:
    experiments_progress = get_experiments_progress(quiet)
    jobs_progress = get_jobs_progress(quiet)
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(experiments_progress, title="Overall progress", padding=(1, 2)),
        Panel.fit(jobs_progress, title="Task progress", padding=(1, 2)),
    )
    return (
        Live(progress_table, console=None if not quiet else Console(quiet=True)),
        experiments_progress,
        jobs_progress,
    )


def get_dataset_sync_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        DownloadColumn(),
        disable=quiet,
    )


def get_sized_dataset_fetch_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        DownloadColumn(),
        disable=quiet,
    )


def get_unsized_dataset_fetch_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        TimeElapsedColumn(),
        FileSizeColumn(),
        disable=quiet,
    )


def get_image_upload_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        ImageDownloadUploadColumn(),
        disable=quiet,
    )


def get_image_download_progress(quiet: bool = False) -> Progress:
    return get_image_upload_progress(quiet)
