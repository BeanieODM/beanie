from typing import Any, Type

import pydantic
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pydantic import BaseModel


def is_version_valid(version, requirement):
    # Parse the requirement as a SpecifierSet
    specifiers = SpecifierSet(requirement)
    # Parse the version as a Version
    v = Version(version)
    # Check if the version satisfies the specifiers
    return v in specifiers


IS_PYDANTIC_V2 = is_version_valid(pydantic.VERSION, ">=2")
IS_PYDANTIC_V2_10 = is_version_valid(pydantic.VERSION, ">=2.10")

if IS_PYDANTIC_V2:
    from pydantic import TypeAdapter
else:
    from pydantic import parse_obj_as


def parse_object_as(object_type: Type, data: Any):
    if IS_PYDANTIC_V2:
        return TypeAdapter(object_type).validate_python(data)
    else:
        return parse_obj_as(object_type, data)


def get_field_type(field):
    if IS_PYDANTIC_V2:
        return field.annotation
    else:
        return field.outer_type_


def get_model_fields(model):
    if IS_PYDANTIC_V2:
        return model.model_fields
    else:
        return model.__fields__


def parse_model(model_type: Type[BaseModel], data: Any):
    if IS_PYDANTIC_V2:
        return model_type.model_validate(data)
    else:
        return model_type.parse_obj(data)


def get_extra_field_info(field, parameter: str):
    if IS_PYDANTIC_V2:
        if isinstance(field.json_schema_extra, dict):
            return field.json_schema_extra.get(parameter)
        return None
    else:
        return field.field_info.extra.get(parameter)


def get_config_value(model, parameter: str):
    if IS_PYDANTIC_V2:
        return model.model_config.get(parameter)
    else:
        return getattr(model.Config, parameter, None)


def get_model_dump(model, *args: Any, **kwargs: Any):
    if IS_PYDANTIC_V2:
        return model.model_dump(*args, **kwargs)
    else:
        return model.dict(*args, **kwargs)
