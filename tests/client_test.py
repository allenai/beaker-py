import pytest

from beaker.client import Beaker


@pytest.fixture(scope="module")
def client():
    return Beaker.from_env()


def test_whoami(client):
    r = client.whoami()
    assert r["institution"] == "AllenAI"
