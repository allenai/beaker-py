from beaker import Beaker, CurrentJobStatus, JobKind


def test_job_get(client: Beaker, hello_world_job_id):
    job = client.job.get(hello_world_job_id)
    assert job.id == hello_world_job_id
    assert job.status.current == CurrentJobStatus.finalized
    assert job.kind == JobKind.execution
    assert job.to_json()["kind"] == "execution"


def test_job_results(client: Beaker, hello_world_job_id):
    results = client.job.results(hello_world_job_id)
    assert results is not None
