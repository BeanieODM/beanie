from datetime import datetime, date

from bson import Binary

from beanie.sync.odm.utils.encoder import Encoder
from tests.sync.models import (
    DocumentForEncodingTest,
    DocumentForEncodingTestDate,
)


def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTest(datetime_field=datetime.now())
    doc.insert()
    new_doc = DocumentForEncodingTest.get(doc.id).run()
    assert isinstance(new_doc.datetime_field, datetime)


def test_encode_date():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTestDate()
    doc.insert()
    new_doc = DocumentForEncodingTestDate.get(doc.id).run()
    assert new_doc.date_field == doc.date_field
    assert isinstance(new_doc.date_field, date)


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


def test_bytes():
    encoded_b = Encoder().encode(b"test")
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 0

    doc = DocumentForEncodingTest(bytes_field=b"test")
    doc.insert()
    new_doc = DocumentForEncodingTest.get(doc.id).run()
    assert isinstance(new_doc.bytes_field, bytes)


def test_bytes_already_binary():
    b = Binary(b"123", 3)
    encoded_b = Encoder().encode(b)
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 3
