from beaker import Beaker, Organization


def test_cluster_get_cloud(client: Beaker, beaker_cluster_name: str):
    assert client.cluster.get(beaker_cluster_name).autoscale is True


def test_cluster_get_on_prem(client: Beaker, beaker_on_prem_cluster_name: str):
    assert client.cluster.get(beaker_on_prem_cluster_name).autoscale is False


def test_cluster_list(client: Beaker, beaker_org: Organization):
    client.cluster.list(beaker_org)


def test_cluster_nodes(client: Beaker, beaker_on_prem_cluster_name: str):
    client.cluster.nodes(beaker_on_prem_cluster_name)
