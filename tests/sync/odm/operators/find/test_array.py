from beanie.odm.operators.find.array import All, ElemMatch, Size
from tests.sync.models import Sample


def test_all():
    q = All(Sample.integer, [1, 2, 3])
    assert q == {"integer": {"$all": [1, 2, 3]}}


def test_elem_match():
    q = ElemMatch(Sample.integer, {"a": "b"})
    assert q == {"integer": {"$elemMatch": {"a": "b"}}}


def test_size():
    q = Size(Sample.integer, 4)
    assert q == {"integer": {"$size": 4}}
