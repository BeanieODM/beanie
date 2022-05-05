from typing import Any, Type, Union, TYPE_CHECKING

from pydantic import BaseModel

from beanie.exceptions import (
    UnionHasNoRegisteredDocs,
    DocWasNotRegisteredInUnionClass,
)
from beanie.odm.interfaces.detector import ModelType

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def parse_obj(
    model: Union[Type[BaseModel], Type["Document"]], data: Any
) -> BaseModel:
    if model.get_model_type() == ModelType.UnionDoc:
        if model._document_models is None:
            raise UnionHasNoRegisteredDocs

        if isinstance(data, dict):
            if data["_class_name"] not in model._document_models:
                raise DocWasNotRegisteredInUnionClass
            return parse_obj(
                model=model._document_models[data["_class_name"]], data=data
            )

    if hasattr(model, "_parse_obj_saving_state"):
        return model._parse_obj_saving_state(data)  # type: ignore
    return model.parse_obj(data)
