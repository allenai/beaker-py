from beaker.client import Beaker


def test_dataset_get(client: Beaker, squad_dataset_name: str):
    dataset = client.dataset.get(squad_dataset_name)
    assert dataset.name is not None
    # Try with ID.
    client.dataset.get(dataset.id)
    # Try with just name (without account prefix).
    client.dataset.get(dataset.name)


def test_file_info(client: Beaker, squad_dataset_name: str, squad_dataset_file_name: str):
    client.dataset.file_info(squad_dataset_name, squad_dataset_file_name)
