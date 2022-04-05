import uuid
from pathlib import Path
from typing import Generator

import petname
import pytest

from beaker.client import Beaker
from beaker.exceptions import DatasetNotFound, ExperimentNotFound, ImageNotFound


@pytest.fixture()
def workspace_name(doctest_namespace) -> str:
    workspace = "ai2/petew-testing"
    doctest_namespace["workspace_name"] = workspace
    return workspace


@pytest.fixture()
def client(doctest_namespace, workspace_name):
    beaker_client = Beaker.from_env(default_workspace=workspace_name)
    doctest_namespace["beaker"] = beaker_client
    return beaker_client


@pytest.fixture()
def docker_image_name(doctest_namespace, client: Beaker):
    image = "hello-world"
    client.docker.images.pull(image)
    doctest_namespace["docker_image_name"] = image
    return image


@pytest.fixture()
def beaker_image_name(doctest_namespace, client: Beaker) -> Generator[str, None, None]:
    image = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["beaker_image_name"] = image
    yield image
    try:
        client.image.delete(f"{client.account.whoami().name}/{image}")
    except ImageNotFound:
        pass


@pytest.fixture()
def beaker_cluster_name(doctest_namespace) -> str:
    cluster = "ai2/petew-cpu"
    doctest_namespace["beaker_cluster_name"] = cluster
    return cluster


@pytest.fixture()
def experiment_name(doctest_namespace, client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["experiment_name"] = name
    yield name
    try:
        client.experiment.delete(f"{client.account.whoami().name}/{name}")
    except ExperimentNotFound:
        pass


@pytest.fixture()
def dataset_name(doctest_namespace, client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["dataset_name"] = name
    yield name
    try:
        client.dataset.delete(f"{client.account.whoami().name}/{name}")
    except DatasetNotFound:
        pass


@pytest.fixture()
def download_path(doctest_namespace, dataset_name, tmp_path) -> Path:
    path = tmp_path / dataset_name
    doctest_namespace["download_path"] = path
    return path
