import pytest

from beaker import (
    Beaker,
    ClusterNotFound,
    CurrentJobStatus,
    DataMount,
    DatasetNotFound,
    DataSource,
    ExperimentSpec,
    ImageNotFound,
    ImageSource,
    ResultSpec,
    SecretNotFound,
    TaskContext,
    TaskNotFound,
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


def test_experiment_metrics_none(client: Beaker, hello_world_experiment_id: str):
    metrics = client.experiment.metrics(hello_world_experiment_id)
    assert metrics is None


def test_experiment_metrics(client: Beaker, experiment_id_with_metrics: str):
    metrics = client.experiment.metrics(experiment_id_with_metrics)
    assert metrics is not None


def test_experiment_results(client, experiment_id_with_results: str):
    results = client.experiment.results(experiment_id_with_results)
    assert results is not None
    assert client.dataset.size(results) > 0


def test_experiment_empty_results(client: Beaker, hello_world_experiment_id: str):
    results = client.experiment.results(hello_world_experiment_id)
    assert results is not None
    assert client.dataset.size(results) == 0


def test_experiment_spec(client: Beaker, hello_world_experiment_id: str):
    spec = client.experiment.spec(hello_world_experiment_id)
    assert isinstance(spec, ExperimentSpec)


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


def test_experiment_url(client: Beaker, hello_world_experiment_id: str):
    assert (
        client.experiment.url(hello_world_experiment_id)
        == "https://beaker.org/ex/01FPB5WGRTM33P5AE6A28MT8QF"
    )
    assert (
        client.experiment.url(hello_world_experiment_id, "main")
        == "https://beaker.org/ex/01FPB5WGRTM33P5AE6A28MT8QF/tasks/01FPB5WGTFQH7K1NM2M1KMZA78"
    )
    with pytest.raises(TaskNotFound, match="No task"):
        client.experiment.url(hello_world_experiment_id, "foo")
