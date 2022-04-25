from beaker import Beaker


def test_str_method(client: Beaker):
    assert "user_token=***" in str(client.config)
    assert client.config.user_token not in str(client.config)
