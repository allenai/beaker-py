import pytest
import yaml

from beaker import Beaker
from beaker.config import Config


def test_str_method(client: Beaker):
    assert "user_token=***" in str(client.config)
    assert client.config.user_token not in str(client.config)


def test_config_from_path_unknown_field(tmp_path):
    path = tmp_path / "config.yml"
    with open(path, "w") as f:
        yaml.dump({"user_token": "foo-bar", "baz": 1}, f)

    with pytest.warns(RuntimeWarning, match="Unknown field 'baz' found in config"):
        Config.from_path(path)
