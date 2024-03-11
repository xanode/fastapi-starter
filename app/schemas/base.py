from copy import deepcopy
from datetime import datetime
from operator import ge, gt, le, lt, ne
from typing import Any, Optional

from humps import camelize
from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo


class DefaultModel(BaseModel):
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)


ExcludedField = Field(default=None, exclude=True)
"""
Excluded field is used when a field is not needed in the response,
but is needed to compute other fields.
"""


class HTTPError(BaseModel):
    detail: str = Field(..., description="Error message.")


class OptionalModel(DefaultModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for field in cls.model_fields.values():
            field.default = None
            field.annotation = Optional[field.annotation]  # type: ignore

        cls.model_rebuild(force=True)


ComparaisonDict = {
    "gt": gt,
    "lt": lt,
    "gte": ge,
    "lte": le,
    "ne": ne,
}
ComparaisonTypes = (
    int,
    float,
    datetime,
    Optional[int],
    Optional[float],
    Optional[datetime],
)


class ComparaisonModel(OptionalModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        fields_extended_with_comparison: dict[str, FieldInfo] = {}

        for name, field in cls.model_fields.items():
            if field.annotation in ComparaisonTypes:
                for suffix, _ in ComparaisonDict.items():
                    field_copy = deepcopy(field)
                    field_copy.alias = f"{name}__{suffix}"
                    field_copy.default = None
                    fields_extended_with_comparison[field_copy.alias] = field_copy

        cls.model_fields.update(fields_extended_with_comparison)
        cls.model_rebuild(force=True)
