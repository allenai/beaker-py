import pytest

from beaker import (
    Beaker,
    ExperimentConflict,
    ExperimentNotFound,
    ExperimentSpec,
    ImageSource,
    ResultSpec,
    TaskContext,
    TaskSpec,
)


def test_experiment_workflow(
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
    experiment = client.experiment.wait_for(experiment, timeout=60 * 3)[0]

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
