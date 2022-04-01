import pytest

from beaker.client import Beaker


@pytest.fixture(autouse=True)
def client(doctest_namespace):
    beaker_client = Beaker.from_env(default_workspace="ai2/beaker-py")
    doctest_namespace["beaker"] = beaker_client
    return beaker_client
