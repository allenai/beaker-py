from beaker import Beaker, CurrentJobStatus, JobKind, JobNotFound


def test_job_get(client: Beaker, hello_world_job_id: str):
    job = client.job.get(hello_world_job_id)
    assert job.id == hello_world_job_id
    assert job.status.current == CurrentJobStatus.finalized
    assert job.kind == JobKind.execution
    assert job.to_json()["kind"] == "execution"


def test_job_results(client: Beaker, hello_world_job_id: str):
    client.job.results(hello_world_job_id)


def test_job_logs(client: Beaker, hello_world_job_id: str):
    logs = "\n".join(
        [
            line.strip()
            for line in b"".join(list(client.job.logs(hello_world_job_id, quiet=True)))
            .decode()
            .split("\n")
        ]
    )
    assert "Hello from Docker!" in logs


def test_job_logs_since(client: Beaker, hello_world_job_id: str):
    logs = "\n".join(
        [
            line.strip()
            for line in b"".join(
                list(
                    client.job.logs(
                        hello_world_job_id, quiet=True, since="2023-02-11T00:34:19.938308862Z"
                    )
                )
            )
            .decode()
            .split("\n")
        ]
    )
    assert "Hello from Docker!" not in logs


def test_summarized_job_events(client: Beaker):
    client.job.summarized_events("01JSCFT1563SA35GXS206J575B")

    try:
        client.job.summarized_events("blah")
    except JobNotFound:
        pass
