import pytest

from beanie.odm.operators.find.logical import And, Nor, Not, Or
from tests.odm.models import Sample


def test_and():
    q = And(Sample.integer == 1)
    assert q == {"integer": 1}

    q = And(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}


async def test_not(preset_documents):
    q = Not(Sample.integer == 1)
    assert q == {"integer": {"$not": {"$eq": 1}}}

    docs = await Sample.find(q).to_list()
    assert len(docs) == 7

    q = Not(And(Sample.integer == 1, Sample.nested.integer > 3))
    with pytest.raises(AttributeError):
        await Sample.find(q).to_list()


def test_nor():
    q = Nor(Sample.integer == 1)
    assert q == {"$nor": [{"integer": 1}]}

    q = Nor(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$nor": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}


def test_or():
    q = Or(Sample.integer == 1)
    assert q == {"integer": 1}

    q = Or(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$or": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}


def test_or_with_bool():
    """Test that Or() properly handles single bool expression (issue #1000)."""
    q = Or(True)
    assert q == {"$or": [True]}
    assert q.query == {"$or": [True]}

    q = Or(False)
    assert q == {"$or": [False]}
    assert q.query == {"$or": [False]}


def test_and_with_bool():
    """Test that And() properly handles single bool expression (issue #1000)."""
    q = And(True)
    assert q == {"$and": [True]}
    assert q.query == {"$and": [True]}

    q = And(False)
    assert q == {"$and": [False]}
    assert q.query == {"$and": [False]}
