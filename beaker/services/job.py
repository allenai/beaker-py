import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generator, List, Optional, Set, Union

import grpc
from rich.progress import Progress, TaskID

from .. import beaker_pb2 as pb2
from ..data_model import *
from ..exceptions import *
from ..progress import get_jobs_progress, get_logs_progress
from ..util import format_since, log_and_wait, protobuf_to_json_dict, split_timestamp
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                exceptions_for_status={404: JobNotFound(job_id)},
            ).json()
        )

    def list(
        self,
        *,
        author: Optional[Union[str, Account]] = None,
        cluster: Optional[Union[str, Cluster]] = None,
        experiment: Optional[Union[str, Experiment]] = None,
        finalized: bool = False,
        kind: Optional[JobKind] = None,
        node: Optional[Union[str, Node]] = None,
    ) -> List[Job]:
        """
        List jobs.

        :param author: List only jobs by particular author.
        :param cluster: List jobs on a particular cluster.
        :param experiment: List jobs in an experiment.
        :param finalized: List only finalized or non-finalized jobs.
        :param kind: List jobs of a certain kind.
        :param node: List jobs on a particular node.

        .. important::
            Either ``cluster``, ``author``, ``experiment``, or ``node`` must be specified.
            If ``node`` is specified, neither ``cluster`` nor ``experiment`` can be
            specified.

        :raises ValueError: If the arguments are invalid, e.g. both ``node`` and
            ``cluster`` are specified.
        :raises AccountNotFound: If the specified author doesn't exist.
        :raises ClusterNotFound: If the specified cluster doesn't exist.
        :raises ExperimentNotFound: If the specified experiment doesn't exist.
        :raises NodeNotFound: If the specified node doesn't exist.
        """
        if node is None and cluster is None and experiment is None and author is None:
            raise ValueError("You must specify one of 'node', 'cluster', 'experiment', or 'author'")

        # Validate arguments.
        if node is not None:
            if cluster is not None:
                raise ValueError("You cannot specify both 'node' and 'cluster'")
            if experiment is not None:
                raise ValueError("You cannot specify both 'node' and 'experiment'")

        jobs: List[Job] = []

        # Build request options.
        request_opts: Dict[str, Any] = {}
        if author is not None:
            author_id = (
                author.id if isinstance(author, Account) else self.beaker.account.get(author).id
            )
            request_opts["author"] = author_id
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
            if not page.next and not page.next_cursor:
                break
            else:
                request_opts["cursor"] = page.next or page.next_cursor

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
            (e.g. "2013-01-02T13:23:37Z"), or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).

        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        job_id = job.id if isinstance(job, Job) else job
        opts = {}
        if since is not None:
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
        with get_logs_progress(quiet) as progress:
            task_id = progress.add_task("Downloading:")
            total = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    advance = len(chunk)
                    total += advance
                    progress.update(task_id, total=total + 1, advance=advance)
                    yield chunk

    def structured_logs(
        self,
        job: Union[str, Job],
        quiet: bool = False,
        since: Optional[Union[datetime, timedelta]] = None,
        tail_lines: Optional[int] = None,
        follow: Optional[bool] = None,
    ) -> Generator[JobLog, None, None]:
        """
        Download/stream structured :class:`~beaker.data_model.job.JobLog` objects from a job using the RPC interface.

        Returns a generator of log objects.

        .. seealso::
            :meth:`logs()`

        .. seealso::
            :meth:`follow()`

        :param job: The Beaker job ID or object.
        :param quiet: If ``True``, progress won't be displayed.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC) or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).
        :param tail_lines: Start tailing with the last ``tail_lines`` lines.
        :param follow: Keep streaming as new log lines come in.

        :raises JobNotFound: If the job can't be found.
        :raises RpcError: Any other RPC error.
        """
        job_id = job.id if isinstance(job, Job) else job

        with self.rpc_connection() as service:
            opts: Dict[str, Any] = {}
            if since is not None:
                opts["since"] = since if isinstance(since, datetime) else datetime.utcnow() - since
            if tail_lines is not None:
                opts["tail_lines"] = tail_lines
            if follow is not None:
                opts["follow"] = follow

            request = pb2.StreamJobLogsRequest(job_id=job_id, **opts)
            with get_logs_progress(quiet, by_line=True) as progress:
                task_id = progress.add_task("Downloading logs:")
                for data in self.rpc_streaming_request(
                    service.StreamJobLogs,
                    request,
                    pb2.JobLog,
                    exceptions_for_status={grpc.StatusCode.NOT_FOUND: JobNotFound(job_id)},
                ):
                    progress.update(task_id, advance=1)
                    yield JobLog(
                        message=data.message.decode(),
                        timestamp=datetime.fromtimestamp(data.timestamp.seconds).replace(
                            microsecond=data.timestamp.nanos // 1_000, tzinfo=timezone.utc
                        ),
                    )

    def metrics(self, job: Union[str, Job]) -> Optional[Dict[str, Any]]:
        """
        Get the metrics from a job.

        .. seealso::
            :meth:`Beaker.experiment.metrics() <ExperimentClient.metrics>`

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        job = job if isinstance(job, Job) else self.get(job)
        if job.result is None or job.result.beaker is None:
            return None
        else:
            try:
                return self.beaker.dataset.get(job.result.beaker)
            except DatasetNotFound:
                return None

    def finalize(self, job: Union[str, Job]) -> Job:
        """
        Finalize a job.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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

    def preempt(self, job: Union[str, Job]) -> Job:
        """
        Preempt a job.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        job_id = job.id if isinstance(job, Job) else job
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                method="PATCH",
                exceptions_for_status={404: JobNotFound(job_id)},
                data=JobPatch(
                    status=JobStatusUpdate(
                        canceled=True,
                        canceled_code=CanceledCode.user_preemption,
                        canceled_for=f"Preempted by user '{self.beaker.account.name}'",
                    )
                ),
            ).json()
        )

    def stop(self, job: Union[str, Job]) -> Job:
        """
        Stop a job.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If the job can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        job_id = job.id if isinstance(job, Job) else job
        return Job.from_json(
            self.request(
                f"jobs/{job_id}",
                method="PATCH",
                exceptions_for_status={404: JobNotFound(job_id)},
                data=JobPatch(
                    status=JobStatusUpdate(
                        canceled=True, canceled_for=f"Stopped by user '{self.beaker.account.name}'"
                    )
                ),
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
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
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        yield from self._as_completed(
            *jobs,
            timeout=timeout,
            poll_interval=poll_interval,
            quiet=quiet,
            strict=strict,
        )

    def follow(
        self,
        job: Union[str, Job],
        timeout: Optional[float] = None,
        strict: bool = False,
        include_timestamps: bool = True,
        since: Optional[Union[str, datetime, timedelta]] = None,
    ) -> Generator[bytes, None, Job]:
        """
        Follow a job live, creating a generator that produces log lines (as bytes) from the job
        as they become available. The return value of the generator is the finalized
        :class:`~beaker.data_model.job.Job` object.

        .. seealso::
            :meth:`follow_structured()`

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
        :param include_timestamps: If ``True`` (the default) timestamps from the Beaker logs
            will be included in the output.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC), a timestamp string in the form of RFC 3339
            (e.g. "2013-01-02T13:23:37Z"), or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).

        :raises JobNotFound: If any job can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.

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
        last_timestamp: Optional[str] = None if since is None else format_since(since)
        lines_for_timestamp: Dict[str, Set[bytes]] = defaultdict(set)

        def get_line_to_yield(line: bytes) -> Optional[bytes]:
            nonlocal last_timestamp, lines_for_timestamp
            timestamp = split_timestamp(line)
            if timestamp is not None and timestamp != last_timestamp:
                last_timestamp = timestamp
                if include_timestamps:
                    return line
                else:
                    return line[len(timestamp) + 1 :]
            elif timestamp is None and last_timestamp is not None:
                if line not in lines_for_timestamp[last_timestamp]:
                    lines_for_timestamp[last_timestamp].add(line)
                    return line
            return None

        def pull_logs_since(updated_job: Job, final: bool = False):
            retries = 0
            while True:
                try:
                    buffer = b""
                    for chunk in self.logs(updated_job, quiet=True, since=last_timestamp):
                        lines = (buffer + chunk).splitlines(keepends=True)
                        if chunk.endswith(b"\n"):
                            buffer = b""
                        elif lines:
                            # Last line in chunk is not a complete line.
                            lines, buffer = lines[:-1], lines[-1]
                        for line in lines:
                            line_to_yield = get_line_to_yield(line)
                            if line_to_yield is not None:
                                yield line_to_yield
                    if final and buffer:
                        line_to_yield = get_line_to_yield(buffer + b"\n")
                        if line_to_yield is not None:
                            yield line_to_yield
                    break
                except RequestException as err:
                    if retries < self.beaker.MAX_RETRIES:
                        log_and_wait(retries, err)
                        retries += 1
                    else:
                        raise

        updated_job: Job
        while True:
            updated_job = self.get(job.id if isinstance(job, Job) else job)

            # Pull and yield log lines.
            for line in pull_logs_since(updated_job):
                yield line

            # Check status of job, finish if job is no-longer running.
            if updated_job.is_finalized:
                break

            # Check timeout if we're still waiting for job to complete.
            if timeout is not None and time.monotonic() - start >= timeout:
                raise JobTimeoutError(updated_job.id)

            time.sleep(1.0)

        for line in pull_logs_since(updated_job, final=True):
            yield line

        if strict:
            updated_job.check()

        return updated_job

    def follow_structured(
        self,
        job: Union[str, Job],
        timeout: Optional[float] = None,
        strict: bool = False,
        since: Optional[Union[datetime, timedelta]] = None,
        tail_lines: Optional[int] = None,
    ) -> Generator[JobLog, None, Job]:
        """
        Follow structured :class:`~beaker.data_model.job.JobLog` objects from a job using the RPC interface.
        The return value of the generator is the finalized :class:`~beaker.data_model.job.Job` object.

        .. seealso::
            :meth:`structured_logs()`

        .. seealso::
            :meth:`follow()`

        :param job: Job ID, name, or object.
        :param timeout: Maximum amount of time to follow job for (in seconds).
        :param strict: If ``True``, the exit code of each job will be checked, and a
            :class:`~beaker.exceptions.JobFailedError` will be raised for non-zero exit codes.
        :param since: Only show logs since a particular time. Could be a :class:`~datetime.datetime` object
            (naive datetimes will be treated as UTC) or a :class:`~datetime.timedelta`
            (e.g. `timedelta(seconds=60)`, which will show you the logs beginning 60 seconds ago).
        :param tail_lines: Start tailing with the last ``tail_lines`` lines.

        :raises JobNotFound: If any job can't be found.
        :raises JobTimeoutError: If the ``timeout`` expires.
        :raises JobFailedError: If ``strict=True`` and any job finishes with a non-zero exit code.
        :raises RpcError: Any other RPC error.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("'timeout' must be a positive number")

        start = time.monotonic()
        job = self.get(job.id if isinstance(job, Job) else job)

        for job_log in self.structured_logs(
            job, quiet=True, since=since, tail_lines=tail_lines, follow=True
        ):
            yield job_log

            # Check timeout if we're still waiting for job to complete.
            if timeout is not None and time.monotonic() - start >= timeout:
                raise JobTimeoutError(job.id)

        if strict:
            job.check()

        return job

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
                    if not job.is_finalized:
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

    def summarized_events(self, job: Union[str, Job]) -> List[SummarizedJobEvent]:
        """
        Get a list of summarized job events.

        :param job: The Beaker job ID or object.

        :raises JobNotFound: If any job can't be found.
        :raises RpcError: Any other RPC error.
        """
        job_id = job.id if isinstance(job, Job) else job
        with self.rpc_connection() as service:
            response = self.rpc_request(
                service.ListSummarizedJobEvents,
                pb2.ListSummarizedJobEventsRequest(
                    options=pb2.ListSummarizedJobEventsRequest.Opts(job_id=job_id)
                ),
                pb2.ListSummarizedJobEventsResponse,
                exceptions_for_status={grpc.StatusCode.NOT_FOUND: JobNotFound(job_id)},
            )
            return [
                SummarizedJobEvent.from_json(protobuf_to_json_dict(d))
                for d in response.summarized_job_events
            ]

    def url(self, job: Union[str, Job]) -> str:
        job_id = job.id if isinstance(job, Job) else job
        return f"{self.config.agent_address}/job/{self.url_quote(job_id)}"
