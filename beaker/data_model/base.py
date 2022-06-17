import logging
from enum import Enum
from typing import Any, Dict, Iterator, Mapping, Sequence, Type, TypeVar, Union

from pydantic import BaseModel as _BaseModel
from pydantic import ValidationError, root_validator

from ..util import to_lower_camel, to_snake_case

T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseModel(_BaseModel):
    """
    The base class for all Beaker data models.
    """

    class Config:
        validate_assignment = True
        use_enum_values = True
        frozen = True

    @root_validator(pre=True)
    def _rename_to_snake_case(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raw data from the Beaker server will use lower camel case.
        """
        return {to_snake_case(k): v for k, v in values.items()}

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
        return self.jsonify(self)

    @classmethod
    def jsonify(cls, x: Any) -> Any:
        if isinstance(x, BaseModel):
            return {
                to_lower_camel(key): cls.jsonify(value) for key, value in x if value is not None
            }
        elif isinstance(x, Enum):
            return cls.jsonify(x.value)
        elif isinstance(x, (str, float, int, bool)):
            return x
        elif isinstance(x, dict):
            return {key: cls.jsonify(value) for key, value in x.items()}
        elif isinstance(x, (list, tuple, set)):
            return [cls.jsonify(x_i) for x_i in x]
        else:
            return x


class MappedSequence(Sequence[T], Mapping[str, T]):
    def __init__(self, sequence: Sequence[T], mapping: Mapping[str, T]):
        self._sequence = sequence
        self._mapping = mapping

    def __getitem__(self, k) -> Union[T, Sequence[T]]:  # type: ignore[override]
        if isinstance(k, (int, slice)):
            return self._sequence[k]
        elif isinstance(k, str):
            return self._mapping[k]
        else:
            raise TypeError("keys must be integers, slices, or strings")

    def __contains__(self, k) -> bool:
        if isinstance(k, str):
            return k in self._mapping
        else:
            return k in self._sequence

    def __iter__(self) -> Iterator[T]:
        return iter(self._sequence)

    def __len__(self) -> int:
        return len(self._sequence)

    def keys(self):
        return self._mapping.keys()

    def values(self):
        return self._mapping.values()
