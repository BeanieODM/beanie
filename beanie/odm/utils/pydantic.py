from typing import Any, Type

import pydantic
from pydantic import BaseModel

IS_PYDANTIC_V2 = int(pydantic.VERSION.split(".")[0]) >= 2

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
        if field.json_schema_extra is not None:
            return field.json_schema_extra.get(parameter)
        return None
    else:
        return field.field_info.extra.get(parameter)


def get_config_value(model, parameter: str):
    if IS_PYDANTIC_V2:
        return model.model_config.get(parameter)
    else:
        return getattr(model.Config, parameter, None)


def get_model_dump(model):
    if IS_PYDANTIC_V2:
        return model.model_dump()
    else:
        return model.dict()


def get_iterator(model, by_alias=False):
    if IS_PYDANTIC_V2:

        def _get_alias(model, k):
            v = model.model_fields.get(k)
            if v is not None:
                return v.alias or k
            else:
                return k

        def _iter(model, by_alias=False):
            for k, v in model.__iter__():
                if by_alias:
                    yield _get_alias(model, k), v
                else:
                    yield k, v

        return _iter(model, by_alias=by_alias)
    else:
        return model._iter(to_dict=False, by_alias=by_alias)
