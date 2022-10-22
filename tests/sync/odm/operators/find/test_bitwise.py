from beanie.odm.operators.find.bitwise import (
    BitsAllClear,
    BitsAllSet,
    BitsAnyClear,
    BitsAnySet,
)
from tests.sync.models import Sample


def test_bits_all_clear():
    q = BitsAllClear(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAllClear": "smth"}}


def test_bits_all_set():
    q = BitsAllSet(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAllSet": "smth"}}


def test_any_clear():
    q = BitsAnyClear(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAnyClear": "smth"}}


def test_any_set():
    q = BitsAnySet(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAnySet": "smth"}}
