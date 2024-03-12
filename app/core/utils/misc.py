import logging
from enum import Enum
from typing import Any, Dict, List, Type

from pydantic import ConfigDict

from app.schemas.base import ComparaisonDict, ComparaisonModel, DefaultModel, OptionalModel

logger = logging.getLogger("app.core.utils.misc")


def to_query_parameters(
    model: type[DefaultModel],
    comparaison: bool = False,
    exclude: list[str] | None = None,
) -> type[DefaultModel]:
    if exclude is None:
        exclude = []

    exclude.extend(["id", "password"])

    # Create a new class which inherit from the model and the ComparaisonModel
    NewModel: type[DefaultModel] = type(
        f"Query{model.__name__}",
        (model, ComparaisonModel if comparaison else OptionalModel),
        {},
    )

    for key in exclude:
        if key in NewModel.model_fields:
            del NewModel.model_fields[key]

    NewModel.model_config = ConfigDict(alias_generator=lambda x: x, populate_by_name=True)
    NewModel.model_rebuild(force=True)

    return NewModel


def process_query_parameters(query_model: DefaultModel) -> dict[str, Any]:
    """
    Function that processes the query parameters.
    If comparison is True, there are multiple fields for comparison, like key__gt and key__lt.
    They will be converted as follows:
    key: {
        ">": value of key__gt,
        "<": value of key__lt
    }

    :param query_model: The query parameters
    :return: The processed query parameters
    """
    query_parameters = query_model.model_dump(exclude_none=True, exclude_unset=True)
    processed_query_parameters: dict[str, Any] = {}
    for key, value in query_parameters.items():
        if "__" in key:
            # If key is in the form of key__gt, key__lt, key__contains, etc.
            # Convert it to key: {">": value of key__gt, "<": value of key__lt}
            key, operator = key.split("__")

            if key not in processed_query_parameters:
                processed_query_parameters[key] = {}

            if operator in ComparaisonDict:
                processed_query_parameters[key][ComparaisonDict[operator]] = value
            else:
                logger.warning(f"Unknown operator {operator} for key {key}")
        else:
            processed_query_parameters[key] = value
    return processed_query_parameters


def create_hierarchy_dict(enum: Type[Enum]) -> Dict[str, List[str]]:
    """
    Takes an Enum class and returns a dictionary mapping Enum values to lists of their ancestors in the Enum hierarchy.

    :param enum: The Enum class. It must have integer values and string names.
    :return: The dictionary mapping Enum values to lists of their ancestors in the Enum hierarchy
    """
    hierarchy_dict = {}
    for e in enum:
        # Get the list of ancestors for the current Enum value
        ancestors = [ancestor.name for ancestor in e.__class__ if ancestor.value < e.value]
        # Add the current Enum value to the list of ancestors
        ancestors.append(e.name)
        # Add the list of ancestors to the hierarchy dictionary
        hierarchy_dict[e.name] = ancestors
    return hierarchy_dict
