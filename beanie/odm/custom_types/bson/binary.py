from typing import Annotated, Any

import bson
import pydantic


def _to_bson_binary(value: Any) -> bson.Binary:
    return value if isinstance(value, bson.Binary) else bson.Binary(value)


BsonBinary = Annotated[bson.Binary, pydantic.PlainValidator(_to_bson_binary)]

__all__ = ["BsonBinary"]
