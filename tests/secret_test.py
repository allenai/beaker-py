from beaker import Beaker


def test_secrets(client: Beaker, secret_name: str):
    secret = client.secret.write(secret_name, "foo")
    assert secret.name == secret_name
    assert client.secret.get(secret_name) == secret
    assert client.secret.read(secret) == "foo"
