import pytest

from beaker import Beaker, GroupConflict, GroupNotFound


def test_group_methods(
    client: Beaker, group_name: str, alternate_group_name: str, hello_world_experiment_id: str
):
    # Create a new group.
    group = client.group.create(group_name)
    assert group.name == group_name

    # Add an experiment to the group.
    client.group.add_experiments(group, hello_world_experiment_id)
    assert len(client.group.list_experiments(group)) == 1

    # Export the experiments from the group
    # (expect a three line CSV: the header, one experiment, and a trailing newline)
    export = list(client.group.export_experiments(group))
    assert len(export) == 1
    assert len(export[0].decode().split("\n")) == 3

    # Remove the experiment from the group.
    client.group.remove_experiments(group, hello_world_experiment_id)
    assert len(client.group.list_experiments(group)) == 0

    # Rename the group.
    group = client.group.rename(group, alternate_group_name)
    assert group.name == alternate_group_name

    # Test group not found error.
    with pytest.raises(GroupNotFound):
        client.group.get(group_name)

    # Test group conflict error.
    with pytest.raises(GroupConflict):
        client.group.create(alternate_group_name)

    # List groups in the workspace.
    group_names = [group.name for group in client.workspace.groups()]
    assert alternate_group_name in group_names


def test_group_url(client: Beaker):
    assert (
        client.group.url("petew/bar") == "https://beaker.org/gr/01G0YXMAX2ES9ZGHJM9NVYF5MJ/compare"
    )
