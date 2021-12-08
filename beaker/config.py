import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import ClassVar, Optional

import yaml

from .exceptions import ConfigurationError


@dataclass
class Config:
    user_token: str
    """
    Beaker user token that can be obtained from
    `beaker.org <https://beaker.org/user>`_.
    """

    agent_address: str = "https://beaker.org"
    """
    The address of the Beaker server.
    """

    default_org: Optional[str] = None
    """
    Default Beaker organization to use.
    """

    default_workspace: Optional[str] = None
    """
    Default Beaker workspace to use.
    """

    DEFAULT_CONFIG_LOCATION: ClassVar[Path] = Path.home() / ".beaker" / "config.yml"
    ADDRESS_KEY: ClassVar[str] = "BEAKER_ADDR"
    CONFIG_PATH_KEY: ClassVar[str] = "BEAKER_CONFIG"
    TOKEN_KEY: ClassVar[str] = "BEAKER_TOKEN"

    @classmethod
    def from_env(cls) -> "Config":
        """
        Initialize a config from environment variables or a local config file if one
        can be found.

        .. note::
            Environment variables take precedence over values in the config file.

        """
        config: Config

        path = cls.find_config()
        if path is not None:
            config = cls.from_path(path)
            if cls.TOKEN_KEY in os.environ:
                config.user_token = os.environ[cls.TOKEN_KEY]
        elif cls.TOKEN_KEY in os.environ:
            config = cls(
                user_token=os.environ[cls.TOKEN_KEY],
            )
        else:
            raise ConfigurationError(
                f"Missing config file or environment variable '{cls.TOKEN_KEY}'"
            )

        # Override with environment variables.
        if cls.ADDRESS_KEY in os.environ:
            config.agent_address = os.environ[cls.ADDRESS_KEY]

        return config

    @classmethod
    def from_path(cls, path: Path) -> "Config":
        """
        Initialize a config from a local config file.
        """
        with open(path) as config_file:
            return cls(**yaml.load(config_file, Loader=yaml.SafeLoader))

    def save(self, path: Optional[Path] = None):
        """
        Save the config to the given path.
        """
        path = path or self.DEFAULT_CONFIG_LOCATION
        path.parent.mkdir(parents=True)
        with open(path, "w") as config_file:
            yaml.dump(asdict(self), config_file)

    @classmethod
    def find_config(cls) -> Optional[Path]:
        if cls.CONFIG_PATH_KEY in os.environ:
            path = Path(os.environ[cls.CONFIG_PATH_KEY])
            if path.is_file():
                return path

        if cls.DEFAULT_CONFIG_LOCATION.is_file():
            return cls.DEFAULT_CONFIG_LOCATION

        return None
