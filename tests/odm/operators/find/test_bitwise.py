from beanie.odm.operators.find.bitwise import (
    BitsAllClear,
    BitsAllSet,
    BitsAnyClear,
    BitsAnySet,
)
from tests.odm.models import Sample


async def test_bits_all_clear():
    q = BitsAllClear(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAllClear": "smth"}}


async def test_bits_all_set():
    q = BitsAllSet(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAllSet": "smth"}}


async def test_any_clear():
    q = BitsAnyClear(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAnyClear": "smth"}}


async def test_any_set():
    q = BitsAnySet(Sample.integer, "smth")
    assert q == {"integer": {"$bitsAnySet": "smth"}}
