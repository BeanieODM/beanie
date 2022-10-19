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

    if model.get_settings().single_root_inheritance:
        class_name = None
        # if _class_id has been specified in the projection then there can be children subclasses in the result
        if isinstance(data, dict) and '_class_id' in data:
            class_name = data["_class_id"]
        elif hasattr(data, '_class_id'):
            class_name = data._class_id

        # if class_name is set and differs from queried model then we should parse data as child subclass
        if class_name and class_name != model.__name__:
            for child in model.get_children():
                if child.__name__ == class_name:
                    return parse_obj(model=child, data=data)

    if (
        hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.UnionDoc
    ):
        if model._document_models is None:
            raise UnionHasNoRegisteredDocs

        if isinstance(data, dict):
            class_name = data["_class_id"]
        else:
            class_name = data._class_id

        if class_name not in model._document_models:
            raise DocWasNotRegisteredInUnionClass
        return parse_obj(model=model._document_models[class_name], data=data)

    # if hasattr(model, "_parse_obj_saving_state"):
    #     return model._parse_obj_saving_state(data)  # type: ignore

    # FIXME: if fetch_links is True and document contains links, they cannot be properly distinguished
    # FIXME: we need to check this before call pydantic's `model.parse_obj` method or implement a wrapper
    return model.parse_obj(data)
