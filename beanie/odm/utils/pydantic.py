from typing import Any

from pydantic import BaseModel, TypeAdapter


def parse_object_as(object_type: type, data: Any):
    return TypeAdapter(object_type).validate_python(data)


def get_field_type(field: Any):
    return field.annotation


def get_model_fields(model: Any):
    if not isinstance(model, type):
        model = model.__class__
    return model.model_fields


def parse_model(model_type: type[BaseModel], data: Any):
    return model_type.model_validate(data)


def get_extra_field_info(field: Any, parameter: str):
    if isinstance(field.json_schema_extra, dict):
        return field.json_schema_extra.get(parameter)
    return None


def get_config_value(model: Any, parameter: str):
    return model.model_config.get(parameter)


def get_model_dump(model: Any, *args: Any, **kwargs: Any):
    return model.model_dump(*args, **kwargs)
