from beaker import Beaker


def test_image_get(client: Beaker, hello_world_image_name: str):
    # Get by full name.
    image = client.image.get(hello_world_image_name)
    # Get by ID.
    client.image.get(image.id)
    # Get by name.
    assert image.name is not None
    client.image.get(image.name)


def test_image_url(client: Beaker, hello_world_image_name: str):
    assert (
        client.image.url(hello_world_image_name)
        == "https://beaker.org/im/01FPB7XCX3GHKW5PS9J4623EBN"
    )
