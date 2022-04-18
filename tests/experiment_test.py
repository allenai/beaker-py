import pytest

from beaker import (
    Beaker,
    ClusterNotFound,
    CurrentJobStatus,
    DataMount,
    Dataset,
    DatasetNotFound,
    DataSource,
    ExperimentConflict,
    ExperimentNotFound,
    ExperimentSpec,
    ImageNotFound,
    ImageSource,
    ResultSpec,
    SecretNotFound,
    Task,
    TaskContext,
    TaskSpec,
)


def test_experiment_get(client: Beaker, hello_world_experiment_id: str):
    exp = client.experiment.get(hello_world_experiment_id)
    assert exp.id == hello_world_experiment_id
    assert exp.jobs
    assert exp.jobs[0].status.current == CurrentJobStatus.finalized
    # Get with name.
    client.experiment.get(exp.name)
    # Get with full name.
    client.experiment.get(exp.full_name)


def test_experiment_tasks(client: Beaker, hello_world_experiment_id: str):
    tasks = client.experiment.tasks(hello_world_experiment_id)
    assert len(tasks) == 1


def test_experiment_results(client: Beaker, hello_world_experiment_id: str):
    results = client.experiment.results(hello_world_experiment_id)
    assert len(results) == 1
    task, results = results[0]
    assert isinstance(task, Task)
    assert isinstance(results, Dataset)
    assert client.dataset.size(results) == 0


def test_experiment_spec(client: Beaker, hello_world_experiment_id: str):
    spec = client.experiment.spec(hello_world_experiment_id)
    assert isinstance(spec, ExperimentSpec)


def test_experiment_create_await_rename(
    client: Beaker,
    experiment_name: str,
    alternate_experiment_name: str,
    beaker_cluster_name: str,
    hello_world_experiment_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(docker="hello-world"),
                context=TaskContext(cluster=beaker_cluster_name),
                result=ResultSpec(path="/unused"),  # required even if the task produces no output.
            ),
        ],
    )
    # Create the experiment.
    experiment = client.experiment.create(experiment_name, spec)

    # Wait for it to finish.
    experiment = client.experiment.await_all(experiment, timeout=60 * 3)[0]

    # Get the logs.
    logs = "".join([line.decode() for line in client.experiment.logs(experiment)])
    assert logs

    # Test experiment conflict error with rename.
    with pytest.raises(ExperimentConflict):
        client.experiment.rename(experiment, hello_world_experiment_name)

    # Rename the experiment.
    experiment = client.experiment.rename(experiment, alternate_experiment_name)
    assert experiment.name == alternate_experiment_name

    # Test experiment not found error.
    with pytest.raises(ExperimentNotFound):
        client.experiment.get(experiment_name)


def test_create_experiment_image_not_found(
    client: Beaker,
    experiment_name: str,
    beaker_cluster_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(beaker="does-not-exist"),
                context=TaskContext(cluster=beaker_cluster_name),
                result=ResultSpec(path="/unused"),
            ),
        ],
    )
    with pytest.raises(ImageNotFound):
        client.experiment.create(experiment_name, spec)


def test_create_experiment_dataset_not_found(
    client: Beaker,
    experiment_name: str,
    beaker_cluster_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(docker="hello-world"),
                context=TaskContext(cluster=beaker_cluster_name),
                result=ResultSpec(path="/unused"),
                datasets=[
                    DataMount(source=DataSource(beaker="does-not-exist"), mount_path="/data")
                ],
            ),
        ],
    )
    with pytest.raises(DatasetNotFound):
        client.experiment.create(experiment_name, spec)


def test_create_experiment_secret_not_found(
    client: Beaker,
    experiment_name: str,
    beaker_cluster_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(docker="hello-world"),
                context=TaskContext(cluster=beaker_cluster_name),
                result=ResultSpec(path="/unused"),
                datasets=[
                    DataMount(source=DataSource(secret="does-not-exist"), mount_path="/data")
                ],
            ),
        ],
    )
    with pytest.raises(SecretNotFound):
        client.experiment.create(experiment_name, spec)


def test_create_experiment_result_not_found(
    client: Beaker,
    experiment_name: str,
    beaker_cluster_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(docker="hello-world"),
                context=TaskContext(cluster=beaker_cluster_name),
                result=ResultSpec(path="/unused"),
                datasets=[
                    DataMount(source=DataSource(result="does-not-exist"), mount_path="/data")
                ],
            ),
        ],
    )
    with pytest.raises(ValueError, match="does-not-exist"):
        client.experiment.create(experiment_name, spec)


def test_create_experiment_cluster_not_found(
    client: Beaker,
    experiment_name: str,
):
    spec = ExperimentSpec(
        tasks=[
            TaskSpec(
                name="main",
                image=ImageSource(docker="hello-world"),
                context=TaskContext(cluster="does-not-exist"),
                result=ResultSpec(path="/unused"),
            ),
        ],
    )
    with pytest.raises(ClusterNotFound):
        client.experiment.create(experiment_name, spec)
