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
    model: Union[Type[BaseModel], Type["Document"]],
    data: Any,
    lazy_parse: bool = False,
) -> BaseModel:
    if (
        hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.UnionDoc  # type: ignore
    ):
        if model._document_models is None:  # type: ignore
            raise UnionHasNoRegisteredDocs

        if isinstance(data, dict):
            class_name = data["_class_id"]
        else:
            class_name = data._class_id

        if class_name not in model._document_models:  # type: ignore
            raise DocWasNotRegisteredInUnionClass
        return parse_obj(
            model=model._document_models[class_name],
            data=data,
            lazy_parse=lazy_parse,
        )  # type: ignore
    if (
        hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.Document  # type: ignore
        and model._inheritance_inited  # type: ignore
    ):
        if isinstance(data, dict):
            class_name = data.get("_class_id")
        elif hasattr(data, "_class_id"):
            class_name = data._class_id
        else:
            class_name = None

        if model._children and class_name in model._children:  # type: ignore
            return parse_obj(
                model=model._children[class_name],
                data=data,
                lazy_parse=lazy_parse,
            )  # type: ignore

    # if hasattr(model, "_parse_obj_saving_state"):
    #     return model._parse_obj_saving_state(data)  # type: ignore
    if (
        lazy_parse
        and hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.Document
    ):
        o = model.construct(
            **{
                "_store": {},
            }
        )
        o.id = data.get("_id")
        if model.get_settings().use_state_management:
            o._save_state()
        o.set_store(data)
        o._lazily_parsed = True
        return o
    return model.parse_obj(data)
