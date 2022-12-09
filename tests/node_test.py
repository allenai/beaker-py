from beaker import Beaker


def test_node_get(client: Beaker, beaker_node_id: str):
    gpu_count = client.node.get(beaker_node_id).limits.gpu_count
    assert gpu_count is not None
    assert gpu_count > 0
