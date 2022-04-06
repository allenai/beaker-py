import io
from typing import Optional

from rich.progress import DownloadColumn, Progress, Task, TaskID
from rich.text import Text


class DownloadUploadColumn(DownloadColumn):
    def render(self, task: Task) -> Text:
        if int(task.total) == 1:
            return Text("")
        else:
            return super().render(task)


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


def to_lower_camel(s: str) -> str:
    """
    Convert a snake-case string into lower camel case.
    """
    parts = s.split("_")
    return parts[0] + "".join([p.title() for p in parts[1:]])


def to_snake_case(s: str) -> str:
    """
    Convert a lower camel case strings into snake case.
    """
    parts = []
    for c in s:
        if c.isupper():
            parts.append("_")
        parts.append(c.lower())
    return "".join(parts)
