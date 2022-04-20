import logging
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel as _BaseModel
from pydantic import ValidationError, root_validator

from ..util import to_lower_camel

T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseModel(_BaseModel):
    """
    The base class for all Beaker data models.
    """

    class Config:
        validate_assignment = True
        alias_generator = to_lower_camel
        use_enum_values = True
        #  extra = "forbid"

    @root_validator(pre=True)
    def _rename_to_alias(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Required since Pydantic only allows to instantiate a model using field aliases.
        """
        return {to_lower_camel(k): v for k, v in values.items()}

    def __getitem__(self, key):
        try:
            return self.dict()[key]
        except KeyError:
            if not key.islower():
                snake_case_key = ""
                for c in key:
                    if c.isupper():
                        snake_case_key += "_"
                    snake_case_key += c.lower()
                try:
                    return self.dict()[snake_case_key]
                except KeyError:
                    pass
            raise

    @classmethod
    def from_json(cls: Type[T], json_data: Dict[str, Any]) -> T:
        try:
            return cls(**json_data)
        except ValidationError:
            logger.error("Error validating raw JSON data for %s: %s", cls.__name__, json_data)
            raise

    def to_json(self) -> Dict[str, Any]:
        return self.dict(by_alias=True, exclude_none=True)
