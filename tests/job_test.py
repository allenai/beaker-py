import time

from beaker import Beaker, CurrentJobStatus, ExperimentSpec, JobKind, TaskSpec


def test_job_get(client: Beaker, hello_world_job_id):
    job = client.job.get(hello_world_job_id)
    assert job.id == hello_world_job_id
    assert job.status.current == CurrentJobStatus.finalized
    assert job.kind == JobKind.execution
    assert job.to_json()["kind"] == "execution"


def test_job_results(client: Beaker, hello_world_job_id):
    results = client.job.results(hello_world_job_id)
    assert results is not None


def test_job_stop_and_finalize(client: Beaker, experiment_name: str, beaker_cluster_name: str):
    start = time.time()
    spec = ExperimentSpec().with_task(
        TaskSpec.new(
            "main",
            beaker_cluster_name,
            docker_image="hello-world",
        ),
    )
    experiment = client.experiment.create(experiment_name, spec)
    while not experiment.jobs:
        experiment = client.experiment.get(experiment.id)
        if time.time() - start > 360:
            raise TimeoutError
    client.job.stop(experiment.jobs[0])
    job = client.job.finalize(experiment.jobs[0])
    assert job.status.current == CurrentJobStatus.finalized
