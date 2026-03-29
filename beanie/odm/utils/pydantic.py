from typing import Any

from pydantic import BaseModel, TypeAdapter
from pydantic.fields import ComputedFieldInfo


def parse_object_as(object_type: type, data: Any):
    return TypeAdapter(object_type).validate_python(data)


def get_field_type(field):
    if isinstance(field, ComputedFieldInfo):
        return field.return_type
    else:
        return field.annotation


def get_model_fields(model):
    if not isinstance(model, type):
        model = model.__class__
    return {**model.model_fields, **model.model_computed_fields}


def get_model_all_items(model):
    return {
        **dict(model.__iter__()),
        **{
            key: getattr(model, key)
            for key in {
                **model.__class__.model_computed_fields,
            }.keys()
        },
    }


def parse_model(model_type: type[BaseModel], data: Any):
    return model_type.model_validate(data)


def get_extra_field_info(field, parameter: str):
    if isinstance(field.json_schema_extra, dict):
        return field.json_schema_extra.get(parameter)
    return None


def get_config_value(model, parameter: str):
    return model.model_config.get(parameter)


def get_model_dump(model, *args: Any, **kwargs: Any):
    return model.model_dump(*args, **kwargs)
