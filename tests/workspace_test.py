from typing import Optional

import pytest

from beaker.client import Beaker


def test_ensure_workspace_invalid_name(client: Beaker):
    with pytest.raises(ValueError, match="Invalided workspace name"):
        client.workspace.ensure("blah")


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


def test_workspace_images(client: Beaker, hello_world_image_name: str):
    images = client.workspace.images(match=hello_world_image_name)
    assert images


def test_workspace_list(client: Beaker, workspace_name: str):
    workspaces = client.workspace.list("ai2", match=workspace_name.split("/")[1])
    assert workspaces
