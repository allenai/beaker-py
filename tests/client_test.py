import pytest

from beaker.client import Beaker


def test_ensure_workspace_invalid_name(client: Beaker):
    with pytest.raises(ValueError, match="Invalided workspace name"):
        client.ensure_workspace("blah")
