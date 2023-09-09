from typing import Any, Callable

import bson
from pydantic import GetJsonSchemaHandler
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class BsonBinary(bson.Binary):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],  # type: ignore
    ) -> core_schema.CoreSchema:  # type: ignore
        def validate(value, _: FieldInfo) -> bson.Binary:
            if isinstance(value, bson.Binary):
                return value
            if isinstance(value, bytes):
                return bson.Binary(value)
            raise ValueError("Value must be bytes or bson.Binary")

        python_schema = core_schema.general_plain_validator_function(validate)  # type: ignore

        return core_schema.json_or_python_schema(
            json_schema=core_schema.float_schema(),
            python_schema=python_schema,
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,  # type: ignore
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())
