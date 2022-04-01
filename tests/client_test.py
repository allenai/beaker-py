import random

import petname
import pytest

from beaker.client import Beaker


def test_whoami(client: Beaker):
    r = client.whoami()
    assert r["institution"] == "AllenAI"


def test_images(client: Beaker):
    client.docker.images.pull("hello-world")
    beaker_image_name = petname.generate() + "-" + str(random.randint(0, 99))
    push_result = client.create_image(beaker_image_name, "hello-world")
    assert push_result["originalTag"] == "hello-world"
    client.delete_image(push_result["id"])


def test_ensure_workspace_invalid_name(client: Beaker):
    with pytest.raises(ValueError, match="Invalided workspace name"):
        client.ensure_workspace("blah")
