import uuid
from pathlib import Path
from typing import Generator

import petname
import pytest

from beaker.client import Beaker
from beaker.exceptions import DatasetNotFound, ExperimentNotFound, ImageNotFound


@pytest.fixture()
def workspace_name() -> str:
    workspace = "ai2/petew-testing"
    return workspace


@pytest.fixture()
def client(workspace_name):
    beaker_client = Beaker.from_env(default_workspace=workspace_name)
    return beaker_client


@pytest.fixture()
def docker_image_name(client: Beaker):
    image = "hello-world"
    client.docker.images.pull(image)
    return image


@pytest.fixture()
def beaker_image_name(client: Beaker) -> Generator[str, None, None]:
    image = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield image
    try:
        client.image.delete(f"{client.account.whoami().name}/{image}")
    except ImageNotFound:
        pass


@pytest.fixture()
def beaker_cluster_name() -> str:
    cluster = "ai2/petew-cpu"
    return cluster


@pytest.fixture()
def experiment_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.experiment.delete(f"{client.account.whoami().name}/{name}")
    except ExperimentNotFound:
        pass


@pytest.fixture()
def dataset_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.dataset.delete(f"{client.account.whoami().name}/{name}")
    except DatasetNotFound:
        pass


@pytest.fixture()
def download_path(dataset_name, tmp_path) -> Path:
    path = tmp_path / dataset_name
    return path
