from beanie.odm.operators.find.element import Exists, Type
from tests.odm.models import Sample


async def test_exists():
    q = Exists(Sample.integer, True)
    assert q == {"integer": {"$exists": True}}

    q = Exists(Sample.integer, False)
    assert q == {"integer": {"$exists": False}}

    q = Exists(Sample.integer)
    assert q == {"integer": {"$exists": True}}


async def test_type():
    q = Type(Sample.integer, "smth")
    assert q == {"integer": {"$type": "smth"}}
