from beanie.odm.query_builder.operators.find.logical import And, Not, Nor, Or
from tests.odm.query_builder.models import A


async def test_and():
    q = And(A.i == 1)
    assert q == {"i": 1}

    q = And(A.i == 1, A.b.i > 3)
    assert q == {"$and": [{"i": 1}, {"b.i": {"$gt": 3}}]}


async def test_not():
    q = Not(A.i == 1)
    assert q == {"$not": {"i": 1}}


async def test_nor():
    q = Nor(A.i == 1)
    assert q == {"$nor": [{"i": 1}]}

    q = Nor(A.i == 1, A.b.i > 3)
    assert q == {"$nor": [{"i": 1}, {"b.i": {"$gt": 3}}]}


async def test_or():
    q = Or(A.i == 1)
    assert q == {"i": 1}

    q = Or(A.i == 1, A.b.i > 3)
    assert q == {"$or": [{"i": 1}, {"b.i": {"$gt": 3}}]}
