from typing import Any

import bson
import pydantic
from typing_extensions import Annotated

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2


def _to_bson_binary(value: Any) -> bson.Binary:
    return value if isinstance(value, bson.Binary) else bson.Binary(value)


if IS_PYDANTIC_V2:
    from pydantic import PlainSerializer

    try:
        import pybase64

        serializer = pybase64.standard_b64encode

    except ImportError:
        import base64
        from warnings import warn

        warn(
            "pybase64 is not installed, using BsonBinary will came with a performance penalty"
        )
        serializer = base64.b64encode

    def to_json_string(value: bson.Binary) -> bytes:
        return serializer(value)

    BsonBinary = Annotated[
        bson.Binary,
        pydantic.PlainValidator(_to_bson_binary),
        PlainSerializer(to_json_string, return_type=bytes, when_used="json"),
    ]
else:

    class BsonBinary(bson.Binary):  # type: ignore[no-redef]
        @classmethod
        def __get_validators__(cls):
            yield _to_bson_binary
