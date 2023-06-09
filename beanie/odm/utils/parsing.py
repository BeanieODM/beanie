from typing import Any, Type, Union, TYPE_CHECKING
from pydantic import BaseModel

from beanie.exceptions import (
    UnionHasNoRegisteredDocs,
    DocWasNotRegisteredInUnionClass,
)
from beanie.odm.interfaces.detector import ModelType

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def merge_models(left: BaseModel, right: BaseModel) -> None:
    from beanie.odm.fields import Link

    if hasattr(left, "_previous_revision_id") and hasattr(
        right, "_previous_revision_id"
    ):
        left._previous_revision_id = right._previous_revision_id  # type: ignore
    for k, right_value in right.__iter__():
        left_value = left.__getattribute__(k)
        if isinstance(right_value, BaseModel) and isinstance(
            left_value, BaseModel
        ):
            merge_models(left_value, right_value)
            continue
        if isinstance(right_value, list):
            links_found = False
            for i in right_value:
                if isinstance(i, Link):
                    links_found = True
                    break
            if links_found:
                continue
        elif not isinstance(right_value, Link):
            left.__setattr__(k, right_value)


def save_state_swap_revision(item: BaseModel):
    if hasattr(item, "_save_state"):
        item._save_state()  # type: ignore
    if hasattr(item, "_swap_revision"):
        item._swap_revision()  # type: ignore


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
            class_name = data[model.get_settings().class_id]  # type: ignore
        else:
            class_name = data._class_id

        if class_name not in model._document_models:  # type: ignore
            raise DocWasNotRegisteredInUnionClass
        return parse_obj(
            model=model._document_models[class_name],  # type: ignore
            data=data,
            lazy_parse=lazy_parse,
        )  # type: ignore
    if (
        hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.Document  # type: ignore
        and model._inheritance_inited  # type: ignore
    ):
        if isinstance(data, dict):
            class_name = data.get(model.get_settings().class_id)  # type: ignore
        elif hasattr(data, model.get_settings().class_id):  # type: ignore
            class_name = data._class_id
        else:
            class_name = None

        if model._children and class_name in model._children:  # type: ignore
            return parse_obj(
                model=model._children[class_name],  # type: ignore
                data=data,
                lazy_parse=lazy_parse,
            )  # type: ignore

    if (
        lazy_parse
        and hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.Document  # type: ignore
    ):
        o = model.lazy_parse(data, {"_id"})  # type: ignore
        o._saved_state = {"_id": o.id}
        return o
    result = model.parse_obj(data)
    save_state_swap_revision(result)
    return result
