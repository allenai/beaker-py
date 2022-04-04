import os
import tempfile

from beaker.client import Beaker, DatasetClient


class TestLargeFileDatasets:
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

    def test_large_file_dataset(self, client: Beaker, dataset_name: str, tmp_path):
        # Create the dataset.
        dataset = client.dataset.create(dataset_name, self.large_file.name, target="large-file.txt")
        assert dataset.name == dataset_name

        # Fetch the dataset.
        client.dataset.fetch(dataset.full_name, target=tmp_path)
        large_file_path = tmp_path / "large-file.txt"
        assert large_file_path.is_file(), f"{list(tmp_path.iterdir())}"
        with open(large_file_path, "rb") as large_file:
            contents = large_file.read()
        assert contents == self.large_file_contents
