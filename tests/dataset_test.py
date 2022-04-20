from beaker.client import Beaker


def test_dataset_get(client: Beaker, squad_dataset_name: str):
    dataset = client.dataset.get(squad_dataset_name)
    # Try with ID.
    client.dataset.get(dataset.id)
    # Try with just name (without account prefix).
    client.dataset.get(dataset.name)
