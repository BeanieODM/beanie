import bson

from beanie import BsonBinary
from tests.odm.models import DocumentWithBsonBinaryField


async def test_bson_binary():
    doc = DocumentWithBsonBinaryField(binary_field=bson.Binary(b"test"))
    await doc.insert()
    assert doc.binary_field == BsonBinary(b"test")

    new_doc = await DocumentWithBsonBinaryField.get(doc.id)
    assert new_doc.binary_field == BsonBinary(b"test")

    doc = DocumentWithBsonBinaryField(binary_field=b"test")
    await doc.insert()
    assert doc.binary_field == BsonBinary(b"test")

    new_doc = await DocumentWithBsonBinaryField.get(doc.id)
    assert new_doc.binary_field == BsonBinary(b"test")
