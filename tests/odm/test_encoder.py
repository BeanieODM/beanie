from datetime import datetime

from bson import Binary

from beanie.odm.utils.encoder import Encoder


def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


def test_bytes():
    assert isinstance(Encoder().encode(b"test"), Binary)
