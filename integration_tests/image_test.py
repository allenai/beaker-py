"""
Tests creating, pushing, and pulling images to/from Beaker.

This requires building a test image called "beaker-py-test" using the Dockerfile
at "test_fixtures/docker/Dockerfile".
"""

from beaker import Beaker

LOCAL_IMAGE_TAG = "beaker-py-test"


def test_image_workflow(client: Beaker, beaker_image_name: str):
    image = client.image.create(beaker_image_name, LOCAL_IMAGE_TAG)
    assert image.original_tag == LOCAL_IMAGE_TAG
