from beanie.odm.operators.find.logical import And, Not, Nor, Or
from tests.odm.models import Sample


async def test_and():
    q = And(Sample.integer == 1)
    assert q == {"integer": 1}

    q = And(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}


async def test_not():
    q = Not(Sample.integer == 1)
    assert q == {"$not": {"integer": 1}}


async def test_nor():
    q = Nor(Sample.integer == 1)
    assert q == {"$nor": [{"integer": 1}]}

    q = Nor(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$nor": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}


async def test_or():
    q = Or(Sample.integer == 1)
    assert q == {"integer": 1}

    q = Or(Sample.integer == 1, Sample.nested.integer > 3)
    assert q == {"$or": [{"integer": 1}, {"nested.integer": {"$gt": 3}}]}
