import logging
from enum import Enum
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import ValidationError

from ..util import to_lower_camel, to_snake_case

try:
    from pydantic import field_validator, model_validator

    from ._base_v2 import BaseModelV2 as _BaseModel
except ImportError:
    from ._base_v1 import BaseModelV1 as _BaseModel  # type: ignore
    from ._base_v1 import field_validator, model_validator  # type: ignore

T = TypeVar("T")

logger = logging.getLogger("beaker")


__all__ = [
    "BaseModel",
    "MappedSequence",
    "StrEnum",
    "IntEnum",
    "BasePage",
    "field_validator",
    "model_validator",
]


class BaseModel(_BaseModel):  # type: ignore
    """
    The base class for all Beaker data models.
    """

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, key):
        try:
            return self.model_dump()[key]  # type: ignore
        except KeyError:
            if not key.islower():
                snake_case_key = to_snake_case(key)
                try:
                    return self.model_dump()[snake_case_key]  # type: ignore
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
                to_lower_camel(key): cls.jsonify(value) for key, value in x if value is not None  # type: ignore
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


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class IntEnum(int, Enum):
    def __str__(self) -> str:
        return str(self.value)


class BasePage(BaseModel, Generic[T]):
    data: Tuple[T, ...]
    next_cursor: Optional[str] = None
    next: Optional[str] = None
