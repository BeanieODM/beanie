# check python version
import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from decimal import Decimal as NativeDecimal
from typing import Any, Callable

from bson import Decimal128
from pydantic import GetJsonSchemaHandler
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class DecimalCustomAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],  # type: ignore
    ) -> core_schema.CoreSchema:  # type: ignore
        def validate(value, _: FieldInfo) -> NativeDecimal:
            if isinstance(value, Decimal128):
                return value.to_decimal()
            return value

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
        return handler(core_schema.float_schema())


DecimalAnnotation = Annotated[NativeDecimal, DecimalCustomAnnotation]
