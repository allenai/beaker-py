from beaker import Beaker


def test_node_get(client: Beaker, beaker_node_id: str):
    assert client.node.get(beaker_node_id).limits.gpu_count == 8
