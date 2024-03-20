from beaker.client import Beaker


def test_create_upload_commit(client: Beaker, dataset_name: str):
    ds = client.dataset.create(dataset_name, commit=False)
    client.dataset.upload(ds, b"foo-bar", "foo-bar")
    client.dataset.commit(ds)
    client.dataset.ls(ds)
    client.dataset.file_info(ds, "foo-bar")
