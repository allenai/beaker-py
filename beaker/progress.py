import io
import time
from typing import Optional, Tuple

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


class DownloadUploadColumn(DownloadColumn):
    def render(self, task: Task) -> Text:
        if int(task.total) == 1:
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
        total = max(0, task.total)
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
    def __init__(self, buffered_reader: io.BufferedReader, progress: Progress, task_id: TaskID):
        super().__init__(buffered_reader.raw)
        self.buffered_reader = buffered_reader
        self.progress = progress
        self.task_id = task_id
        self.total_read = 0

    def peek(self, size: int = 0) -> bytes:
        return self.buffered_reader.peek(size)

    def read(self, size: Optional[int] = None) -> bytes:
        out = self.buffered_reader.read(size)
        self.progress.advance(self.task_id, len(out))
        self.total_read += len(out)
        return out

    def read1(self, size: int = -1) -> bytes:
        out = self.buffered_reader.read1(size)
        self.progress.advance(self.task_id, len(out))
        self.total_read += len(out)
        return out


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
        DownloadUploadColumn(),
        disable=quiet,
    )


def get_sized_dataset_fetch_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        DownloadUploadColumn(),
        disable=quiet,
    )


def get_unsized_dataset_fetch_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        TimeElapsedColumn(),
        DownloadUploadColumn(),
        disable=quiet,
    )


def get_image_upload_progress(quiet: bool = False) -> Progress:
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        DownloadUploadColumn(),
        disable=quiet,
    )


def get_image_download_progress(quiet: bool = False) -> Progress:
    return get_image_upload_progress(quiet)
