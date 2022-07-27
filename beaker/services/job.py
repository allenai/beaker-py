import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient

if TYPE_CHECKING:
    from rich.progress import Progress, TaskID


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
        :param finalized: List only finalized or non-finalized jobs.
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

    def logs(
        self,
        job: Union[str, Job],
        quiet: bool = False,
        since: Optional[Union[str, datetime, timedelta]] = None,
    ) -> Generator[bytes, None, None]:
        """
        Download the logs for a job.

        Returns a generator with the streaming bytes from the download.
        The generator should be exhausted, otherwise the logs downloaded will be incomplete.

        .. seealso::
            :meth:`Beaker.experiment.logs() <ExperimentClient.logs>`

        .. seealso::
            :meth:`follow()`

        :param job: The Beaker job ID or object.
        :param quiet: If ``True``, progress won't be displayed.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC), a timestamp string in the form of RFC 3339
            (e.g. "2013-01-02T13:23:37Z"), or a relative time
            (e.g. a :class:`~datetime.timedelta` or a string like "42m").

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job_id = job.id if isinstance(job, Job) else job
        opts = {}
        if since is not None:
            from ..util import format_since

            opts["since"] = format_since(since)

        response = self.request(
            f"jobs/{job_id}/logs",
            method="GET",
            exceptions_for_status={404: JobNotFound(job_id)},
            stream=True,
            query=opts,
        )

        # TODO: currently beaker doesn't provide the Content-Length header, update this if they do.
        #  content_length = response.headers.get("Content-Length")
        #  total = int(content_length) if content_length is not None else None

        from ..progress import get_logs_progress

        with get_logs_progress(quiet) as progress:
            task_id = progress.add_task("Downloading:")
            total = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    advance = len(chunk)
                    total += advance
                    progress.update(task_id, total=total + 1, advance=advance)
                    yield chunk

    def metrics(self, job: Union[str, Job]) -> Optional[Dict[str, Any]]:
        """
        Get the metrics from a job.

        .. seealso::
            :meth:`Beaker.experiment.metrics() <ExperimentClient.metrics>`

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job_id = job.id if isinstance(job, Job) else job
        return self.request(
            f"jobs/{job_id}/results",
            method="GET",
            exceptions_for_status={404: JobNotFound(job_id)},
        ).json()["metrics"]

    def results(self, job: Union[str, Job]) -> Optional[Dataset]:
        """
        Get the results from a job.

        .. seealso::
            :meth:`Beaker.experiment.results() <ExperimentClient.results>`

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job: Job = self.get(job.id if isinstance(job, Job) else job)
        if job.execution is None:
            return None
        else:
            return self.beaker.dataset.get(job.execution.result.beaker)

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
                data=JobPatch(status=JobStatusUpdate(finalized=True)),
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
                data=JobPatch(status=JobStatusUpdate(canceled=True)),
            ).json()
        )

    def wait_for(
        self,
        *jobs: Union[str, Job],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0,
        quiet: bool = False,
        strict: bool = False,
    ) -> List[Job]:
        """
        Wait for jobs to finalize, returning the completed jobs as a list in the same order
        they were given as input.

        .. caution::
            This method is experimental and may change or be removed in future releases.

        .. seealso::
            :meth:`as_completed()`

        .. seealso::
            :meth:`follow()`

        .. seealso::
            :meth:`Beaker.experiment.wait_for() <ExperimentClient.wait_for>`

        :param jobs: Job ID, name, or object.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param poll_interval: Time to wait between polling each job's status (in seconds).
        :param quiet: If ``True``, progress won't be displayed.
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.

        :raises JobNotFound: If any job can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises DuplicateJobError: If the same job is given as an argument more than once.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        job_id_to_position: Dict[str, int] = {}
        jobs_to_wait_on: List[Job] = []
        for i, job_ in enumerate(jobs):
            job = job_ if isinstance(job_, Job) else self.get(job_)
            jobs_to_wait_on.append(job)
            if job.id in job_id_to_position:
                raise DuplicateJobError(job.display_name)
            job_id_to_position[job.id] = i
        completed_jobs: List[Job] = list(
            self.as_completed(
                *jobs_to_wait_on,
                timeout=timeout,
                poll_interval=poll_interval,
                quiet=quiet,
                strict=strict,
            )
        )
        return sorted(completed_jobs, key=lambda job: job_id_to_position[job.id])

    def as_completed(
        self,
        *jobs: Union[str, Job],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0,
        quiet: bool = False,
        strict: bool = False,
    ) -> Generator[Job, None, None]:
        """
        Wait for jobs to finalize, returning an iterator that yields jobs as they complete.

        .. caution::
            This method is experimental and may change or be removed in future releases.

        .. seealso::
            :meth:`wait_for()`

        .. seealso::
            :meth:`follow()`

        .. seealso::
            :meth:`Beaker.experiment.as_completed() <ExperimentClient.as_completed>`

        :param jobs: Job ID, name, or object.
        :param timeout: Maximum amount of time to wait for (in seconds).
        :param poll_interval: Time to wait between polling each job's status (in seconds).
        :param quiet: If ``True``, progress won't be displayed.
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.

        :raises JobNotFound: If any job can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises DuplicateJobError: If the same job is given as an argument more than once.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        yield from self._as_completed(
            *jobs,
            timeout=timeout,
            poll_interval=poll_interval,
            quiet=quiet,
            strict=strict,
        )

    def follow(
        self, job: Union[str, Job], timeout: Optional[float] = None, strict: bool = False
    ) -> Generator[bytes, None, Job]:
        """
        Follow a job live, creating a generator that produces log lines (as bytes) from the job
        as they become available. The return value of the generator is the finalized
        :class:`~beaker.data_model.job.Job` object.

        .. seealso::
            :meth:`logs()`

        .. seealso::
            :meth:`wait_for()`

        .. seealso::
            :meth:`as_completed()`

        .. seealso::
            :meth:`Beaker.experiment.follow() <ExperimentClient.follow>`

        :param job: Job ID, name, or object.
        :param timeout: Maximum amount of time to follow job for (in seconds).
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.

        :raises JobNotFound: If any job can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.

        :examples:

        >>> job = beaker.experiment.latest_job(hello_world_experiment_name)
        >>> for line in beaker.job.follow(job):
        ...     # Every log line from Beaker starts with an RFC 3339 UTC timestamp
        ...     # (e.g. '2021-12-07T19:30:24.637600011Z'). If we don't want to print
        ...     # the timestamps we can split them off like this:
        ...     line = line[line.find(b"Z ")+2:]
        ...     print(line.decode(errors="ignore"), end="")
        <BLANKLINE>
        Hello from Docker!
        This message shows that your installation appears to be working correctly.
        <BLANKLINE>
        ...

        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.monotonic()
        last_timestamp: Optional[str] = None

        def pull_logs_since(updated_job: Job):
            nonlocal last_timestamp
            buffer = b""
            for chunk in self.logs(updated_job, quiet=True, since=last_timestamp):
                lines = (buffer + chunk).splitlines(keepends=True)
                if chunk.endswith(b"\n"):
                    buffer = b""
                elif lines:
                    # Last line in chunk is not a complete line.
                    lines, buffer = lines[:-1], lines[-1]
                timestamp: Optional[str] = None
                for line in lines:
                    timestamp_end = line.find(b"Z ")
                    if timestamp_end > 0:
                        timestamp = line[: timestamp_end + 1].decode()
                    else:
                        timestamp = None
                    if last_timestamp is None or timestamp != last_timestamp:
                        # Only yield new lines.
                        yield line
                if timestamp is not None:
                    last_timestamp = timestamp

        updated_job: Job
        while True:
            updated_job = self.get(job.id if isinstance(job, Job) else job)

            # Pull and yield log lines.
            for line in pull_logs_since(updated_job):
                yield line

            # Check status of job, finish if job is no-longer running.
            if updated_job.is_done:
                break

            # Check timeout if we're still waiting for job to complete.
            if timeout is not None and time.monotonic() - start >= timeout:
                raise JobTimeoutError(updated_job.id)

            time.sleep(1.0)

        for line in pull_logs_since(updated_job):
            yield line

        if strict:
            updated_job.check()

        return updated_job

    def _as_completed(
        self,
        *jobs: Union[str, Job],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0,
        quiet: bool = False,
        strict: bool = False,
        _progress: Optional["Progress"] = None,
    ) -> Generator[Job, None, None]:
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        exp_id_to_name: Dict[str, str] = {}
        task_id_to_name: Dict[str, str] = {}

        def display_name(j: Job) -> str:
            if j.execution is None:
                return f"[i]{j.id}[/]"
            else:
                if j.execution.experiment not in exp_id_to_name:
                    exp = self.beaker.experiment.get(j.execution.experiment)
                    exp_id_to_name[exp.id] = exp.name if exp.name is not None else exp.id
                if j.execution.task not in task_id_to_name:
                    for task in self.beaker.experiment.tasks(j.execution.experiment):
                        if task.id not in task_id_to_name:
                            task_id_to_name[task.id] = (
                                task.name if task.name is not None else task.id
                            )
                return (
                    f"[b cyan]{exp_id_to_name[j.execution.experiment]}[/] "
                    f"\N{rightwards arrow} [i]{task_id_to_name[j.execution.task]}[/]"
                )

        from ..progress import get_jobs_progress

        job_ids: List[str] = []
        start = time.monotonic()
        owned_progress = _progress is None
        progress = _progress or get_jobs_progress(quiet)
        if owned_progress:
            progress.start()
        try:
            job_id_to_progress_task: Dict[str, "TaskID"] = {}
            for job_ in jobs:
                job = job_ if isinstance(job_, Job) else self.get(job_)
                job_ids.append(job.id)
                if job.id in job_id_to_progress_task:
                    raise DuplicateJobError(job.id)
                job_id_to_progress_task[job.id] = progress.add_task(f"{display_name(job)}:")

            polls = 0
            while True:
                if not job_id_to_progress_task:
                    yield from []
                    return

                polls += 1

                # Poll each experiment and update the progress line.
                for job_id in list(job_id_to_progress_task):
                    task_id = job_id_to_progress_task[job_id]
                    job = self.get(job_id)
                    if not job.is_done:
                        progress.update(task_id, total=polls + 1, advance=1)
                    else:
                        # Ensure job was successful if `strict==True`.
                        if strict:
                            job.check()
                        progress.update(
                            task_id,
                            total=polls + 1,
                            completed=polls + 1,
                        )
                        progress.stop_task(task_id)
                        del job_id_to_progress_task[job_id]
                        yield job

                elapsed = time.monotonic() - start
                if timeout is not None and elapsed >= timeout:
                    raise JobTimeoutError
                time.sleep(poll_interval)
        finally:
            if owned_progress:
                progress.stop()
