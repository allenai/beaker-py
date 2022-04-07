from beaker import Beaker, CurrentJobStatus


def test_experiment_get(client: Beaker, hello_world_experiment_id):
    exp = client.experiment.get(hello_world_experiment_id)
    assert exp.id == hello_world_experiment_id
    assert exp.jobs
    assert exp.jobs[0].status.current == CurrentJobStatus.finalized
