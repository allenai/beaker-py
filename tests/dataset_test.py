import os
import tempfile

from beaker.client import Beaker, DatasetClient


class TestLargeFileUpload:
    def setup_method(self):
        self.original_size_limit = DatasetClient.REQUEST_SIZE_LIMIT
        DatasetClient.REQUEST_SIZE_LIMIT = 1024
        self.large_file = tempfile.NamedTemporaryFile(delete=False)
        self.large_file.write(b"a" * 1024 * 2)
        self.large_file.close()

    def teardown_method(self):
        DatasetClient.REQUEST_SIZE_LIMIT = self.original_size_limit
        os.remove(self.large_file.name)

    def test_large_file_upload(self, client: Beaker, dataset_name):
        dataset = client.dataset.create(dataset_name, self.large_file.name, target="large-file.txt")
        assert dataset.name == dataset_name
