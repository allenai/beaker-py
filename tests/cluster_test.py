import pytest

from beaker import Beaker, Organization


def test_cluster_get_on_prem(client: Beaker, beaker_on_prem_cluster_name: str):
    cluster = client.cluster.get(beaker_on_prem_cluster_name)
    assert cluster.autoscale is False
    assert cluster.is_cloud is False
    assert cluster.is_active is True
    assert cluster.node_spec is None
    assert cluster.node_shape is None


@pytest.mark.skip(reason="Takes too long")
def test_cluster_utilization(client: Beaker, beaker_on_prem_cluster_name: str):
    client.cluster.utilization(beaker_on_prem_cluster_name)


def test_cluster_list(client: Beaker, beaker_org: Organization):
    client.cluster.list(beaker_org)


def test_cluster_nodes(client: Beaker, beaker_on_prem_cluster_name: str):
    client.cluster.nodes(beaker_on_prem_cluster_name)


def test_cluster_url(client: Beaker):
    assert (
        client.cluster.url("ai2/jupiter-cirrascale-2")
        == "https://beaker.org/cl/ai2/jupiter/details"
    )
