from beanie.odm.operators.find.array import All, ElemMatch, Size
from tests.odm.query_builder.models import Sample


async def test_all():
    q = All(Sample.integer, [1, 2, 3])
    assert q == {"integer": {"$all": [1, 2, 3]}}


async def test_elem_match():
    q = ElemMatch(Sample.integer, {"a": "b"})
    assert q == {"integer": {"$elemMatch": {"a": "b"}}}


async def test_size():
    q = Size(Sample.integer, 4)
    assert q == {"integer": {"$size": 4}}
