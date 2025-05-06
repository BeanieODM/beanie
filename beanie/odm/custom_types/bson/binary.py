from typing import Annotated, Any

from bson import Binary
from pydantic import PlainValidator


def _to_bson_binary(value: Any) -> Binary:
    return value if isinstance(value, Binary) else Binary(value)


BsonBinary = Annotated[Binary, PlainValidator(_to_bson_binary)]

__all__ = ["BsonBinary"]
