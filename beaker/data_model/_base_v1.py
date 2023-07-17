from typing import Any, ClassVar, Dict, Optional, Set, Type

from pydantic import BaseModel as _BaseModel
from pydantic import root_validator, validator

from ..util import issue_data_model_warning, to_snake_case


def field_validator(*fields: str, mode: str = "after"):
    return validator(*fields, pre=mode == "before")


def model_validator(mode: str = "after"):
    return root_validator(pre=mode == "before")  # type: ignore


class BaseModelV1(_BaseModel):
    """
    The Pydantic v1 base class for all Beaker data models.
    """

    class Config:
        validate_assignment = True
        use_enum_values = True
        frozen = True
        extra = "ignore"

    IGNORE_FIELDS: ClassVar[Set[str]] = set()

    @root_validator(pre=True)
    def _validate_and_rename_to_snake_case(  # type: ignore
        cls: Type["BaseModelV1"], values: Dict[str, Any]  # type: ignore
    ) -> Dict[str, Any]:
        """
        Raw data from the Beaker server will use lower camel case.
        """
        # In some cases we get an instance instead of a dict.
        # We'll just punt there and hope for the best.
        if not isinstance(values, dict):
            return values

        as_snake_case = {to_snake_case(k): v for k, v in values.items()}
        for key, value in as_snake_case.items():
            if (
                cls.__config__.extra != "allow"  # type: ignore
                and key not in cls.__fields__  # type: ignore
                and key not in cls.IGNORE_FIELDS
            ):
                issue_data_model_warning(cls, key, value)
        return as_snake_case

    def model_copy(self, update: Optional[Dict[str, Any]] = None, deep: bool = False):
        return self.copy(update=update, deep=deep)

    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)
