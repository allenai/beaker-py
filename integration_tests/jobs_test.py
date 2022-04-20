import time

from beaker import Beaker, ExperimentSpec, TaskSpec


def test_job_stop_and_finalize(client: Beaker, experiment_name: str, beaker_cluster_name: str):
    start = time.time()
    spec = ExperimentSpec().with_task(
        TaskSpec.new(
            "main",
            beaker_cluster_name,
            docker_image="hello-world",
        ),
    )
    print(f"Creating experiment {experiment_name}")
    experiment = client.experiment.create(experiment_name, spec)
    print("Waiting for jobs to register", end="")
    while not experiment.jobs:
        if time.time() - start > (60 * 5):
            raise TimeoutError
        time.sleep(2)
        print(".", end="")
        experiment = client.experiment.get(experiment.id)
    print("\nStopping job")
    client.job.stop(experiment.jobs[0])
    print("Finalizing job")
    job = client.job.finalize(experiment.jobs[0])
    assert job.is_finalized
