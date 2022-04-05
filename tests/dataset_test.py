import os
import tempfile
from pathlib import Path

from beaker.client import Beaker, DatasetClient


class TestLargeFileDataset:
    def setup_method(self):
        self.original_size_limit = DatasetClient.REQUEST_SIZE_LIMIT
        DatasetClient.REQUEST_SIZE_LIMIT = 1024
        self.large_file = tempfile.NamedTemporaryFile(delete=False)
        self.large_file_contents = b"a" * 1024 * 2
        self.large_file.write(self.large_file_contents)
        self.large_file.close()

    def teardown_method(self):
        DatasetClient.REQUEST_SIZE_LIMIT = self.original_size_limit
        os.remove(self.large_file.name)

    def test_large_file_dataset(self, client: Beaker, dataset_name: str, tmp_path: Path):
        # Create the dataset.
        dataset = client.dataset.create(dataset_name, self.large_file.name, target="large-file.txt")
        assert dataset.name == dataset_name

        # Fetch the dataset.
        client.dataset.fetch(dataset, target=tmp_path)
        large_file_path = tmp_path / "large-file.txt"
        assert large_file_path.is_file(), f"{list(tmp_path.iterdir())}"
        with open(large_file_path, "rb") as large_file:
            contents = large_file.read()
        assert contents == self.large_file_contents


class TestManyFilesDataset:
    def test_many_files_dataset(self, client: Beaker, dataset_name: str, tmp_path: Path):
        dir_to_upload = tmp_path / "upload"
        dir_to_upload.mkdir()
        for i in range(100):
            (dir_to_upload / f"file{i}.txt").open("w").write(str(i))

        dataset = client.dataset.create(dataset_name, dir_to_upload)

        download_dir = tmp_path / "download"
        client.dataset.fetch(dataset, target=download_dir)

        for i in range(100):
            downloaded = download_dir / f"file{i}.txt"
            assert downloaded.is_file()
            assert downloaded.open("r").read() == str(i)
