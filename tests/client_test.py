import random

import docker
import petname
import pytest

from beaker.client import Beaker
from beaker.config import Config


@pytest.fixture(scope="module")
def client():
    config = Config.from_env()
    config.default_workspace = "ai2/beaker-py"
    return Beaker(config)


@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()


def test_whoami(client):
    r = client.whoami()
    assert r["institution"] == "AllenAI"


def test_images(client, docker_client):
    docker_client.images.pull("hello-world")
    beaker_image_name = petname.generate() + "-" + str(random.randint(0, 99))
    push_result = client.create_image(beaker_image_name, "hello-world")
    assert push_result["originalTag"] == "hello-world"
    client.delete_image(push_result["id"])
