import uuid
from typing import Generator

import petname
import pytest

from beaker.client import Beaker
from beaker.exceptions import DatasetNotFound, ImageNotFound


@pytest.fixture(autouse=True, scope="module")
def workspace_name(doctest_namespace) -> str:
    workspace = "ai2/petew-testing"
    doctest_namespace["workspace_name"] = workspace
    return workspace


@pytest.fixture(autouse=True, scope="module")
def client(doctest_namespace, workspace_name):
    beaker_client = Beaker.from_env(default_workspace=workspace_name)
    doctest_namespace["beaker"] = beaker_client
    return beaker_client


@pytest.fixture(autouse=True, scope="module")
def docker_image_name(doctest_namespace, client: Beaker):
    image = "hello-world"
    client.docker.images.pull(image)
    doctest_namespace["docker_image_name"] = image
    return image


@pytest.fixture(autouse=True, scope="module")
def beaker_image_name(doctest_namespace, client: Beaker) -> Generator[str, None, None]:
    image = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["beaker_image_name"] = image
    yield image
    try:
        client.delete_image(f"{client.user}/{image}")
    except ImageNotFound:
        pass


@pytest.fixture(autouse=True, scope="module")
def beaker_cluster_name(doctest_namespace) -> str:
    cluster = "ai2/petew-cpu"
    doctest_namespace["beaker_cluster_name"] = cluster
    return cluster


@pytest.fixture(autouse=True, scope="module")
def experiment_name(doctest_namespace) -> str:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["experiment_name"] = name
    return name


@pytest.fixture(autouse=True, scope="module")
def dataset_name(doctest_namespace, client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    doctest_namespace["dataset_name"] = name
    yield name
    try:
        client.delete_dataset(f"{client.user}/{name}")
    except DatasetNotFound:
        pass
