"""
Tests creating, pushing, and pulling images to/from Beaker.

This requires building a test image called "beaker-py-test" using the Dockerfile
at "test_fixtures/docker/Dockerfile".
"""

from beaker import Beaker

LOCAL_IMAGE_TAG = "beaker-py-test"


def test_image_workflow(client: Beaker, beaker_image_name: str, alternate_beaker_image_name: str):
    # Create and push the image.
    print(f"Creating image '{beaker_image_name}'")
    image = client.image.create(beaker_image_name, LOCAL_IMAGE_TAG)
    assert image.name == beaker_image_name
    assert image.original_tag == LOCAL_IMAGE_TAG

    # Rename the image.
    print(f"Renaming image to '{alternate_beaker_image_name}'")
    image = client.image.rename(image, alternate_beaker_image_name)
    assert image.name == alternate_beaker_image_name
