from beaker import Beaker


def test_image_get(client: Beaker, hello_world_image_name: str):
    # Get by full name.
    image = client.image.get(hello_world_image_name)
    # Get by ID.
    client.image.get(image.id)
    # Get by name.
    client.image.get(image.name)
