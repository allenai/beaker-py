import logging
import os
import warnings
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import ClassVar, Optional

import yaml

from .exceptions import ConfigurationError

DEFAULT_CONFIG_LOCATION: Optional[Path] = None
try:
    DEFAULT_CONFIG_LOCATION = Path.home() / ".beaker" / "config.yml"
except RuntimeError:
    # Can't locate home directory.
    pass


__all__ = ["Config"]

logger = logging.getLogger(__name__)


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

    default_image: Optional[str] = None
    """
    The default image used for interactive sessions.
    """

    ADDRESS_KEY: ClassVar[str] = "BEAKER_ADDR"
    CONFIG_PATH_KEY: ClassVar[str] = "BEAKER_CONFIG"
    TOKEN_KEY: ClassVar[str] = "BEAKER_TOKEN"

    def __str__(self) -> str:
        fields_str = "user_token=***, " + ", ".join(
            [f"{f.name}={getattr(self, f.name)}" for f in fields(self) if f.name != "user_token"]
        )
        return f"{self.__class__.__name__}({fields_str})"

    @classmethod
    def from_env(cls, **overrides) -> "Config":
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
        elif "user_token" in overrides:
            config = cls(user_token=overrides["user_token"])
        else:
            raise ConfigurationError(
                f"Failed to find config file or environment variable '{cls.TOKEN_KEY}'"
            )

        # Override with environment variables.
        if cls.ADDRESS_KEY in os.environ:
            config.agent_address = os.environ[cls.ADDRESS_KEY]

        # Override with any arguments passed to this method.
        for name, value in overrides.items():
            if hasattr(config, name):
                setattr(config, name, value)
            else:
                raise ConfigurationError(f"Beaker config has no attribute '{name}'")

        return config

    @classmethod
    def from_path(cls, path: Path) -> "Config":
        """
        Initialize a config from a local config file.
        """
        with open(path) as config_file:
            logger.debug("Loading beaker config from '%s'", path)
            field_names = {f.name for f in fields(cls)}
            data = yaml.load(config_file, Loader=yaml.SafeLoader)
            for key in list(data.keys()):
                value = data[key]
                if key not in field_names:
                    del data[key]
                    warnings.warn(
                        f"Unknown field '{key}' found in config '{path}'. "
                        f"If this is a bug, please report it at https://github.com/allenai/beaker-py/issues/new/",
                        RuntimeWarning,
                    )
                elif isinstance(value, str) and value == "":
                    # Replace empty strings with `None`
                    data[key] = None
            return cls(**data)

    def save(self, path: Optional[Path] = None):
        """
        Save the config to the given path.
        """
        if path is None:
            if self.CONFIG_PATH_KEY in os.environ:
                path = Path(os.environ[self.CONFIG_PATH_KEY])
            elif DEFAULT_CONFIG_LOCATION is not None:
                path = DEFAULT_CONFIG_LOCATION
        if path is None:
            raise ValueError("param 'path' is required")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as config_file:
            yaml.dump(asdict(self), config_file)

    @classmethod
    def find_config(cls) -> Optional[Path]:
        if cls.CONFIG_PATH_KEY in os.environ:
            path = Path(os.environ[cls.CONFIG_PATH_KEY])
            if path.is_file():
                return path
        elif DEFAULT_CONFIG_LOCATION is not None and DEFAULT_CONFIG_LOCATION.is_file():
            return DEFAULT_CONFIG_LOCATION

        return None
