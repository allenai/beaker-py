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
