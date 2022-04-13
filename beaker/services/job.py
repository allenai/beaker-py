from typing import Any, Dict, Generator, Union

from rich.progress import FileSizeColumn, Progress, SpinnerColumn, TimeElapsedColumn

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class JobClient(ServiceClient):
    """
    Accessed via :data:`Beaker.job <beaker.Beaker.job>`.
    """

    def get(self, job_id: str) -> Job:
        """
        Get information about a job.

        :param job_id: The ID of the Beaker job.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                exceptions_for_status={404: JobNotFound(job_id)},
            ).json()
        )

    def list(
        self,
        cluster: Optional[Union[str, Cluster]] = None,
        experiment: Optional[Union[str, Experiment]] = None,
        finalized: bool = False,
        kind: Optional[JobKind] = None,
        node: Optional[Union[str, Node]] = None,
    ) -> List[Job]:
        """
        List jobs.

        :param cluster: List jobs on a cluster.
        :param experiment: List jobs in an experiment.
        :param finalized: List only finalized or unfinalized jobs.
        :param kind: List jobs of a certain kind.
        :param node: List jobs on a node.

        .. important::
            Either ``cluster``, ``experiment``, or ``node`` must be specified.
            If ``node`` is specified, neither ``cluster`` nor ``experiment`` can be
            specified.

        :raises ValueError: If the arguments are invalid, e.g. both ``node`` and
            ``cluster`` are specified.
        :raises ClusterNotFound: If the specified cluster doesn't exist.
        :raises ExperimentNotFound: If the specified experiment doesn't exist.
        :raises NodeNotFound: If the specified node doesn't exist.
        """
        # Validate arguments.
        if node is not None:
            if cluster is not None:
                raise ValueError("You cannot specify both 'node' and 'cluster'")
            if experiment is not None:
                raise ValueError("You cannot specify both 'node' and 'experiment'")
        else:
            if cluster is None and experiment is None:
                raise ValueError("You must specify one of 'node', 'experiment', or 'cluster'")

        jobs: List[Job] = []

        # Build request options.
        request_opts: Dict[str, Any] = {}
        if cluster is not None:
            cluster_id = (
                cluster.id if isinstance(cluster, Cluster) else self.beaker.cluster.get(cluster).id
            )
            request_opts["cluster"] = cluster_id
        if node is not None:
            node_id = node.id if isinstance(node, Node) else self.beaker.node.get(node).id
            request_opts["node"] = node_id
        if experiment is not None:
            exp_id = (
                experiment.id
                if isinstance(experiment, Experiment)
                else self.beaker.experiment.get(experiment).id
            )
            request_opts["experiment"] = exp_id
        if kind is not None:
            request_opts["kind"] = kind.value
        request_opts["finalized"] = finalized

        # Gather jobs, page by page.
        while True:
            page = Jobs.from_json(self.request("jobs", method="GET", query=request_opts).json())
            if page.data:
                jobs.extend(page.data)
            if not page.next:
                break
            else:
                request_opts["cursor"] = page.next

        return jobs

    def logs(self, job: Union[str, Job], quiet: bool = False) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. seealso::
            :meth:`Beaker.experiment.logs() <ExperimentClient.logs>`

        :param job_id: The Beaker job ID or object.
        :param quiet: If ``True``, progress won't be displayed.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        job_id = job.id if isinstance(job, Job) else job
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

    def finalize(self, job: Union[str, Job]) -> Job:
        """
        Finalize a job.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job_id = job.id if isinstance(job, Job) else job
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                method="PATCH",
                exceptions_for_status={404: JobNotFound(job_id)},
                data={"status": {"finalized": True}},
            ).json()
        )

    def stop(self, job: Union[str, Job]) -> Job:
        """
        Stop a job.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job_id = job.id if isinstance(job, Job) else job
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                method="PATCH",
                exceptions_for_status={404: JobNotFound(job_id)},
                data={"status": {"canceled": True}},
            ).json()
        )
