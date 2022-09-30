from beanie.odm_sync.operators.update.bitwise import Bit
from tests.odm_sync.models import Sample


def test_bit():
    q = Bit({Sample.integer: 2})
    assert q == {"$bit": {"integer": 2}}
