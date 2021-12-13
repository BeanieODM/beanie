from datetime import datetime

from bson import Binary

from beanie.odm.utils.encoder import Encoder
from tests.odm.models import DocumentForEncodingTest


async def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTest(datetime_field=datetime.now())
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.datetime_field, datetime)


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


async def test_bytes():
    assert isinstance(Encoder().encode(b"test"), Binary)

    doc = DocumentForEncodingTest(bytes_field=b"test")
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.bytes_field, bytes)
