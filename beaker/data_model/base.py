import logging
import warnings
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel as _BaseModel
from pydantic import ValidationError, root_validator

from ..util import to_lower_camel, to_snake_case

T = TypeVar("T")

logger = logging.getLogger("beaker")


__all__ = ["BaseModel", "MappedSequence", "StrEnum", "IntEnum", "BasePage"]


BUG_REPORT_URL = (
    "https://github.com/allenai/beaker-py/issues/new?assignees=&labels=bug&template=bug_report.yml"
)

_VALIDATION_WARNINGS_ISSUED: Set[Tuple[str, str]] = set()


class BaseModel(_BaseModel):
    """
    The base class for all Beaker data models.
    """

    class Config:
        validate_assignment = True
        use_enum_values = True
        frozen = True

    IGNORE_FIELDS: ClassVar[Set[str]] = set()

    @root_validator(pre=True)
    def _validate_and_rename_to_snake_case(  # type: ignore
        cls: Type["BaseModel"], values: Dict[str, Any]  # type: ignore
    ) -> Dict[str, Any]:
        """
        Raw data from the Beaker server will use lower camel case.
        """
        as_snake_case = {to_snake_case(k): v for k, v in values.items()}
        for key, value in as_snake_case.items():
            if key not in cls.__fields__ and key not in cls.IGNORE_FIELDS:
                warn_about = (cls.__name__, key)
                if warn_about not in _VALIDATION_WARNINGS_ISSUED:
                    _VALIDATION_WARNINGS_ISSUED.add(warn_about)
                    warnings.warn(
                        f"Found unknown field '{key}: {value}' for data model '{cls.__name__}'. "
                        "This may be a newly added field that hasn't been defined in beaker-py yet. "
                        "Please submit an issue report about this here:\n"
                        f"{BUG_REPORT_URL}",
                        RuntimeWarning,
                    )
        return as_snake_case

    def __str__(self) -> str:
        return self.__repr__()

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
