from typing import Optional, Union

import pytest

from beaker import (
    Account,
    Beaker,
    Permission,
    Workspace,
    WorkspaceNotFound,
    WorkspaceWriteError,
)


def test_ensure_workspace_invalid_name(client: Beaker):
    with pytest.raises(ValueError, match="Invalid name"):
        client.workspace.ensure("blah&&")


def test_workspace_get(client: Beaker, workspace_name: str):
    workspace = client.workspace.get(workspace_name)
    # Now get by ID.
    client.workspace.get(workspace.id)
    # Now get by name without the org prefix.
    client.workspace.get(workspace.name)


@pytest.mark.parametrize("match", [pytest.param(v, id=f"match={v}") for v in (None, "squad")])
@pytest.mark.parametrize(
    "results", [pytest.param(v, id=f"results={v}") for v in (None, True, False)]
)
@pytest.mark.parametrize(
    "uncommitted", [pytest.param(v, id=f"uncommitted={v}") for v in (None, True, False)]
)
def test_workspace_datasets(
    client: Beaker, match: Optional[str], results: Optional[bool], uncommitted: Optional[bool]
):
    client.workspace.datasets(match=match, results=results, uncommitted=uncommitted, limit=50)


def test_workspace_experiments(client: Beaker, hello_world_experiment_name: str):
    experiments = client.workspace.experiments(match=hello_world_experiment_name)
    assert experiments


def test_workspace_images(client: Beaker):
    images = client.workspace.images(match="hello-world")
    assert images


def test_workspace_list(client: Beaker, workspace_name: str):
    workspaces = client.workspace.list("ai2", match=workspace_name.split("/")[1])
    assert workspaces


def test_archived_workspace_write_error(client: Beaker, archived_workspace: Workspace):
    with pytest.raises(WorkspaceWriteError):
        client.workspace.archive(archived_workspace)
    with pytest.raises(WorkspaceWriteError):
        client.secret.write("foo", "bar", workspace=archived_workspace)


def test_archived_workspace_read_ok(client: Beaker, archived_workspace: Workspace):
    client.workspace.secrets(archived_workspace)


def test_organization_not_set(client: Beaker, archived_workspace: Workspace):
    client.config.default_org = None
    with pytest.raises(WorkspaceNotFound):
        client.workspace.secrets(archived_workspace.name)


def test_workspace_move(
    client: Beaker, workspace_name: str, alternate_workspace_name: str, dataset_name: str
):
    dataset = client.dataset.create(dataset_name, workspace=alternate_workspace_name)
    assert dataset.workspace_ref.full_name == alternate_workspace_name
    client.workspace.move(dataset)
    assert client.dataset.get(dataset.id).workspace_ref.full_name == workspace_name


def list_objects(client: Beaker, workspace: Optional[Union[str, Workspace]]):
    client.workspace.secrets(workspace=workspace)
    client.workspace.datasets(workspace=workspace, limit=2, results=False)
    client.workspace.experiments(workspace=workspace, limit=2, match="hello-world")
    client.workspace.images(workspace=workspace, limit=2, match="hello-world")


def test_default_workspace_list_objects(client: Beaker):
    list_objects(client, None)


def test_workspace_list_objects_with_id(client: Beaker, alternate_workspace: Workspace):
    list_objects(client, alternate_workspace.id)


def test_workspace_list_objects_with_short_name(client: Beaker, alternate_workspace: Workspace):
    list_objects(client, alternate_workspace.name)


def test_workspace_list_objects_with_full_name(client: Beaker, alternate_workspace: Workspace):
    list_objects(client, alternate_workspace.full_name)


def test_workspace_list_objects_with_object(client: Beaker, alternate_workspace: Workspace):
    list_objects(client, alternate_workspace)


def test_workspace_get_permissions(client: Beaker):
    client.workspace.get_permissions()


def test_workspace_grant_and_revoke_permissions(client: Beaker, alternate_user: Account):
    client.workspace.grant_permissions(Permission.read, alternate_user)
    client.workspace.revoke_permissions(alternate_user)


def test_workspace_set_visibility(client: Beaker):
    client.workspace.set_visibility(public=False)


def test_workspace_set_visibility_archived(client: Beaker, archived_workspace_name: str):
    client.workspace.set_visibility(public=False, workspace=archived_workspace_name)


def test_workspace_url(client: Beaker):
    assert (
        client.workspace.url("ai2/beaker-py-testing")
        == "https://beaker.org/ws/ai2/beaker-py-testing"
    )
