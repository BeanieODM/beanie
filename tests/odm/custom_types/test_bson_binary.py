import bson
import pytest

from beanie import BsonBinary
from beanie.odm.utils.pydantic import get_model_dump, parse_model
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
