from beaker import Beaker, Organization


def test_cluster_get_cloud(client: Beaker, beaker_cloud_cluster_name: str):
    cluster = client.cluster.get(beaker_cloud_cluster_name)
    assert cluster.autoscale is True
    assert cluster.is_cloud is True
    assert cluster.is_active is True
    assert cluster.node_spec is not None
    assert cluster.node_shape is not None
    # Get by ID.
    client.cluster.get(cluster.id)
    # Get by name without org.
    client.cluster.get(cluster.name)


def test_cluster_get_on_prem(client: Beaker, beaker_on_prem_cluster_name: str):
    cluster = client.cluster.get(beaker_on_prem_cluster_name)
    assert cluster.autoscale is False
    assert cluster.is_cloud is False
    assert cluster.is_active is True
    assert cluster.node_spec is None
    assert cluster.node_shape is None


def test_cluster_list(client: Beaker, beaker_org: Organization):
    client.cluster.list(beaker_org)


def test_cluster_nodes(client: Beaker, beaker_on_prem_cluster_name: str):
    client.cluster.nodes(beaker_on_prem_cluster_name)


def test_cluster_url(client: Beaker):
    assert (
        client.cluster.url("ai2/allennlp-cirrascale")
        == "https://beaker.org/cl/ai2/allennlp-cirrascale/details"
    )
