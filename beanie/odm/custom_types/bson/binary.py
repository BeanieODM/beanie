from typing import Any, Callable

import bson
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import GetJsonSchemaHandler
    from pydantic.fields import FieldInfo
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import core_schema


class BsonBinary(bson.Binary):
    if IS_PYDANTIC_V2:

        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],  # type: ignore
        ) -> core_schema.CoreSchema:  # type: ignore
            def validate(value, _: FieldInfo) -> bson.Binary:
                if isinstance(value, BsonBinary):
                    return value
                if isinstance(value, bson.Binary):
                    return BsonBinary(value)
                if isinstance(value, bytes):
                    return BsonBinary(value)
                raise ValueError(
                    "Value must be bytes or bson.Binary or BsonBinary"
                )

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

    else:

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, value):
            if isinstance(value, BsonBinary):
                return value
            if isinstance(value, bson.Binary):
                return BsonBinary(value)
            if isinstance(value, bytes):
                return BsonBinary(value)
            raise ValueError(
                "Value must be bytes or bson.Binary or BsonBinary"
            )
