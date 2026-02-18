from typing import Any, Type

import pydantic
from pydantic import BaseModel, TypeAdapter

IS_PYDANTIC_V2 = int(pydantic.VERSION.split(".")[0]) >= 2
IS_PYDANTIC_V2_10 = (
    IS_PYDANTIC_V2 and int(pydantic.VERSION.split(".")[1]) >= 10
)


def parse_object_as(object_type: Type, data: Any):
    return TypeAdapter(object_type).validate_python(data)


def get_field_type(field):
    return field.annotation


def get_model_fields(model):
    if not isinstance(model, type):
        model = model.__class__
    return model.model_fields


def parse_model(model_type: Type[BaseModel], data: Any):
    return model_type.model_validate(data)


def get_extra_field_info(field, parameter: str):
    if isinstance(field.json_schema_extra, dict):
        return field.json_schema_extra.get(parameter)
    return None


def get_config_value(model, parameter: str):
    return model.model_config.get(parameter)


def get_model_dump(model, *args: Any, **kwargs: Any):
    return model.model_dump(*args, **kwargs)
