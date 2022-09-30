from beanie.odm_sync.operators.find.element import Exists, Type
from tests.odm_sync.models import Sample


def test_exists():
    q = Exists(Sample.integer, True)
    assert q == {"integer": {"$exists": True}}

    q = Exists(Sample.integer, False)
    assert q == {"integer": {"$exists": False}}

    q = Exists(Sample.integer)
    assert q == {"integer": {"$exists": True}}


def test_type():
    q = Type(Sample.integer, "smth")
    assert q == {"integer": {"$type": "smth"}}
