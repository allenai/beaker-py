from typing import Any, ClassVar, Dict, Set, Type

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, model_validator

from ..util import issue_data_model_warning, to_snake_case


class BaseModelV2(_BaseModel):
    """
    The Pydantic v2 base class for a Beaker data models.
    """

    model_config = ConfigDict(
        validate_assignment=True, use_enum_values=True, frozen=True, extra="ignore"
    )

    IGNORE_FIELDS: ClassVar[Set[str]] = set()

    @model_validator(mode="before")
    def _validate_and_rename_to_snake_case(  # type: ignore
        cls: Type["BaseModelV2"], values: Dict[str, Any]  # type: ignore
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
                cls.model_config["extra"] != "allow"  # type: ignore
                and key not in cls.model_fields
                and key not in cls.IGNORE_FIELDS
            ):
                issue_data_model_warning(cls, key, value)
        return as_snake_case
