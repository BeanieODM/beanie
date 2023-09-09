import bson

from tests.odm.models import TestDocumentWithBsonBinaryField


async def test_bson_binary():
    doc = TestDocumentWithBsonBinaryField(binary_field=bson.Binary(b"test"))
    await doc.insert()
    assert doc.binary_field == bson.Binary(b"test")

    new_doc = await TestDocumentWithBsonBinaryField.get(doc.id)
    assert new_doc.binary_field == bson.Binary(b"test")

    doc = TestDocumentWithBsonBinaryField(binary_field=b"test")
    await doc.insert()
    assert doc.binary_field == bson.Binary(b"test")

    new_doc = await TestDocumentWithBsonBinaryField.get(doc.id)
    assert new_doc.binary_field == bson.Binary(b"test")
