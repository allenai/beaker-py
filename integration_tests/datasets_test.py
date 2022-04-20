import os
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from beaker.client import Beaker, DatasetClient
from beaker.exceptions import DatasetWriteError


class TestDataset:
    def setup_method(self):
        self.file_a = tempfile.NamedTemporaryFile(delete=False)
        self.file_a_contents = b"a" * 10
        self.file_a.write(self.file_a_contents)
        self.file_a.close()

        self.file_b = tempfile.NamedTemporaryFile(delete=False)
        self.file_b_contents = b"b" * 10
        self.file_b.write(self.file_b_contents)
        self.file_b.close()

    def teardown_method(self):
        os.remove(self.file_a.name)
        os.remove(self.file_b.name)

    def test_dataset_write_error(self, client: Beaker, dataset_name: str):
        dataset = client.dataset.create(dataset_name, self.file_a.name, commit=True)
        with pytest.raises(DatasetWriteError):
            client.dataset.sync(dataset, self.file_b.name)

    def test_dataset_basics(self, client: Beaker, dataset_name: str, alternate_dataset_name: str):
        dataset = client.dataset.create(
            dataset_name, self.file_a.name, self.file_b.name, commit=True
        )
        assert dataset.name == dataset_name

        # Stream the whole thing at once.
        contents = b"".join(list(client.dataset.stream_file(dataset, Path(self.file_a.name).name)))
        assert contents == self.file_a_contents

        # Stream just part of the file.
        contents = b"".join(
            list(client.dataset.stream_file(dataset, Path(self.file_a.name).name, offset=5))
        )
        assert contents == self.file_a_contents[5:]

        # Calculate the size.
        assert client.dataset.size(dataset) == 20

        # Rename it.
        dataset = client.dataset.rename(dataset, alternate_dataset_name)
        assert dataset.name == alternate_dataset_name


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

    @pytest.mark.parametrize(
        "commit_right_away",
        (pytest.param(True, id="commit now"), pytest.param(False, id="commit later")),
    )
    def test_large_file_dataset(
        self, client: Beaker, dataset_name: str, tmp_path: Path, commit_right_away: bool
    ):
        # Create the dataset.
        dataset = client.dataset.create(
            dataset_name, self.large_file.name, commit=commit_right_away
        )
        if not commit_right_away:
            dataset = client.dataset.commit(dataset)

        # Verify fields.
        assert dataset.name == dataset_name
        assert dataset.committed is not None

        # Fetch the dataset.
        client.dataset.fetch(dataset, target=tmp_path)
        large_file_path = tmp_path / self.large_file.name
        assert large_file_path.is_file(), f"{list(tmp_path.iterdir())}"
        with open(large_file_path, "rb") as large_file:
            contents = large_file.read()
        assert contents == self.large_file_contents


class TestManyFilesDataset:
    @pytest.mark.parametrize(
        "target",
        (pytest.param("target_dir", id="target dir"), pytest.param(None, id="no target dir")),
    )
    def test_many_files_dataset(
        self, client: Beaker, dataset_name: str, tmp_path: Path, target: Optional[str]
    ):
        # Create the local sources.
        dir_to_upload = tmp_path / "dataset_dir"
        dir_to_upload.mkdir()
        for i in range(100):
            (dir_to_upload / f"file{i}.txt").open("w").write(str(i))
        file_to_upload = tmp_path / "dataset_file.txt"
        file_to_upload.open("w").write("Hello, World!")

        # Create the dataset.
        dataset = client.dataset.create(dataset_name, dir_to_upload, file_to_upload, target=target)

        # List files in the dataset.
        files = list(client.dataset.ls(dataset))
        assert len(files) == 101
        for file_info in files:
            if target is not None:
                assert file_info.path.startswith(target)
            assert file_info.path.endswith(".txt")

        # Download the dataset.
        download_dir = tmp_path / "download"
        client.dataset.fetch(dataset, target=download_dir)

        base_dir = download_dir / target if target is not None else download_dir
        for i in range(100):
            if target:
                downloaded = base_dir / f"file{i}.txt"
            else:
                downloaded = base_dir / f"file{i}.txt"
            assert downloaded.is_file()
            assert downloaded.open("r").read() == str(i)
        assert (base_dir / "dataset_file.txt").is_file()
        assert (base_dir / "dataset_file.txt").open("r").read() == "Hello, World!"
