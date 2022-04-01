from rich.progress import DownloadColumn, Task
from rich.text import Text


class DownloadUploadColumn(DownloadColumn):
    def render(self, task: Task) -> Text:
        if int(task.total) == 1:
            return Text("")
        else:
            return super().render(task)
