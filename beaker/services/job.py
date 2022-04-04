from typing import Generator

from rich.progress import FileSizeColumn, Progress, SpinnerColumn, TimeElapsedColumn

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


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
