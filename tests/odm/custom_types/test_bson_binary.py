from base64 import b64encode

import bson
import pytest
from bson import Binary
from pybase64 import standard_b64encode

from beanie import BsonBinary
from beanie.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_model_dump,
    parse_model,
)
from tests.odm.models import DocumentWithBsonBinaryField


@pytest.mark.parametrize("binary_field", [bson.Binary(b"test"), b"test"])
async def test_bson_binary(binary_field):
    doc = DocumentWithBsonBinaryField(binary_field=binary_field)
    await doc.insert()
    assert doc.binary_field == BsonBinary(b"test")

    new_doc = await DocumentWithBsonBinaryField.get(doc.id)
    assert new_doc.binary_field == BsonBinary(b"test")


@pytest.mark.parametrize("binary_field", [bson.Binary(b"test"), b"test"])
def test_bson_binary_roundtrip(binary_field):
    doc = DocumentWithBsonBinaryField(binary_field=binary_field)
    doc_dict = get_model_dump(doc)
    new_doc = parse_model(DocumentWithBsonBinaryField, doc_dict)
    assert new_doc == doc


bad_utf = [
    b"\xed\xa0\x80",  # Start of a surrogate pair without continuation
    b"\xf0\x82\x82\xac",  # Overlong encoding of U+0020AC
    b"\xed\xa0\x80\xed\xbf\xbf",  # Encoded surrogate pair
    b"\xc0\xaf",  # Overlong encoding of '/'
    b"\xe0\x80\xaf",  # Overlong encoding of '/'
    b"\xf0\x8f\xbf\xbf",  # Beyond Unicode range
]


@pytest.mark.parametrize("binary_field", bad_utf)
def test_bson_binary_serialization_of_nonstring_json(binary_field):
    if IS_PYDANTIC_V2:
        data = DocumentWithBsonBinaryField(
            binary_field=binary_field
        ).model_dump(mode="json", exclude={"id"})["binary_field"]
        assert data == b64encode(binary_field).decode("utf-8")
        assert data == standard_b64encode(binary_field).decode("utf-8")


@pytest.mark.parametrize("binary_field", bad_utf)
def test_bson_binary_serialization_of_nonstring_python(binary_field):
    if IS_PYDANTIC_V2:
        assert DocumentWithBsonBinaryField(
            binary_field=binary_field
        ).model_dump(mode="python", exclude={"id"})["binary_field"] == Binary(
            binary_field
        )
