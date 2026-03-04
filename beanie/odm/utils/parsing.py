from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from beanie.exceptions import (
    ApplyChangesException,
    DocWasNotRegisteredInUnionClass,
    UnionHasNoRegisteredDocs,
)
from beanie.odm.utils.pydantic import get_config_value, parse_model

if TYPE_CHECKING:
    from beanie.odm.documents import Document
    from beanie.odm.union_doc import UnionDoc
    from beanie.odm.views import View


def merge_models(left: BaseModel, right: BaseModel) -> None:
    """
    Merge two models
    :param left: left model
    :param right: right model
    :return: None
    """
    from beanie.odm.fields import Link

    for k, right_value in right.__iter__():
        left_value = getattr(left, k, None)
        if isinstance(right_value, BaseModel) and isinstance(
            left_value, BaseModel
        ):
            if get_config_value(left_value, "frozen"):
                left.__setattr__(k, right_value)
            else:
                merge_models(left_value, right_value)
            continue
        if isinstance(right_value, list):
            if any(isinstance(i, Link) for i in right_value):
                continue
            left.__setattr__(k, right_value)
        elif not isinstance(right_value, Link):
            left.__setattr__(k, right_value)


def apply_changes(changes: dict[str, Any], target: BaseModel | dict[str, Any]):
    for key, value in changes.items():
        if "." in key:
            key_parts = key.split(".")
            current_target = target
            try:
                for part in key_parts[:-1]:
                    if isinstance(current_target, dict):
                        current_target = current_target[part]
                    elif isinstance(current_target, BaseModel):
                        current_target = getattr(current_target, part)
                    else:
                        raise ApplyChangesException(
                            f"Unexpected type of target: {type(target)}"
                        )
                final_key = key_parts[-1]
                if isinstance(current_target, dict):
                    current_target[final_key] = value
                elif isinstance(current_target, BaseModel):
                    setattr(current_target, final_key, value)
                else:
                    raise ApplyChangesException(
                        f"Unexpected type of target: {type(target)}"
                    )
            except (KeyError, AttributeError) as e:
                raise ApplyChangesException(
                    f"Failed to apply change for key '{key}': {e}"
                )
        else:
            if isinstance(target, dict):
                target[key] = value
            elif isinstance(target, BaseModel):
                setattr(target, key, value)
            else:
                raise ApplyChangesException(
                    f"Unexpected type of target: {type(target)}"
                )


def save_state(item: BaseModel):
    if hasattr(item, "_save_state"):
        item._save_state()  # type: ignore


def parse_obj(
    model: type[BaseModel] | type["Document | View | UnionDoc"],
    data: Any,
    lazy_parse: bool = False,
) -> BaseModel:
    from beanie import Document, UnionDoc

    if isinstance(model, UnionDoc):
        if model._document_models is None:
            raise UnionHasNoRegisteredDocs

        if isinstance(data, dict):
            class_name = data[model.get_settings().class_id]
        else:
            class_name = data._class_id

        if class_name not in model._document_models:
            raise DocWasNotRegisteredInUnionClass
        return parse_obj(
            model=model._document_models[class_name],
            data=data,
            lazy_parse=lazy_parse,
        )
    elif isinstance(model, Document):
        if model._inheritance_inited:
            if isinstance(data, dict):
                class_name = data.get(model.get_settings().class_id)
            elif hasattr(data, model.get_settings().class_id):
                class_name = data._class_id
            else:
                class_name = None

            if model._children and class_name in model._children:
                return parse_obj(
                    model=model._children[class_name],  # type: ignore
                    data=data,
                    lazy_parse=lazy_parse,
                )
        if lazy_parse:
            o = model.lazy_parse(data, {"_id"})  # type: ignore
            o._saved_state = {"_id": o.id}
            return o
    result = parse_model(model, data)  # pyright: ignore[reportArgumentType]
    save_state(result)
    return result
