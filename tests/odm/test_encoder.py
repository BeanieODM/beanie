from datetime import datetime

from beanie.odm.utils.encoder import Encoder


def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )
