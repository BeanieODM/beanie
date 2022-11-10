from datetime import datetime, date

from bson import Binary

from beanie.odm.utils.encoder import Encoder
from tests.odm.models import (
    DocumentForEncodingTest,
    DocumentForEncodingTestDate,
    SampleWithMutableObjects,
    Child,
)


async def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTest(datetime_field=datetime.now())
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.datetime_field, datetime)


async def test_encode_date():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTestDate()
    await doc.insert()
    new_doc = await DocumentForEncodingTestDate.get(doc.id)
    assert new_doc.date_field == doc.date_field
    assert isinstance(new_doc.date_field, date)


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


async def test_bytes():
    encoded_b = Encoder().encode(b"test")
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 0

    doc = DocumentForEncodingTest(bytes_field=b"test")
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.bytes_field, bytes)


async def test_bytes_already_binary():
    b = Binary(b"123", 3)
    encoded_b = Encoder().encode(b)
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 3


async def test_mutable_objects_on_save():
    instance = SampleWithMutableObjects(
        d={"Bar": Child(child_field="Foo")}, l=[Child(child_field="Bar")]
    )
    await instance.save()
    assert isinstance(instance.d["Bar"], Child)
    assert isinstance(instance.l[0], Child)
