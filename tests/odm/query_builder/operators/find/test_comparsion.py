from beanie.odm.query_builder.operators.find.comparsion import (
    Eq,
    GT,
    GTE,
    In,
    LT,
    LTE,
    NE,
    NotIn,
)
from tests.odm.query_builder.models import A


async def test_eq():
    q = A.i == 1
    assert q == {"i": 1}

    q = Eq(A.i, 1)
    assert q == {"i": 1}

    q = Eq("i", 1)
    assert q == {"i": 1}


async def test_gt():
    q = A.i > 1
    assert q == {"i": {"$gt": 1}}

    q = GT(A.i, 1)
    assert q == {"i": {"$gt": 1}}

    q = GT("i", 1)
    assert q == {"i": {"$gt": 1}}


async def test_gte():
    q = A.i >= 1
    assert q == {"i": {"$gte": 1}}

    q = GTE(A.i, 1)
    assert q == {"i": {"$gte": 1}}

    q = GTE("i", 1)
    assert q == {"i": {"$gte": 1}}


async def test_in():
    q = In(A.i, [1])
    assert q == {"i": {"$in": [1]}}

    q = In(A.i, [1])
    assert q == {"i": {"$in": [1]}}


async def test_lt():
    q = A.i < 1
    assert q == {"i": {"$lt": 1}}

    q = LT(A.i, 1)
    assert q == {"i": {"$lt": 1}}

    q = LT("i", 1)
    assert q == {"i": {"$lt": 1}}


async def test_lte():
    q = A.i <= 1
    assert q == {"i": {"$lte": 1}}

    q = LTE(A.i, 1)
    assert q == {"i": {"$lte": 1}}

    q = LTE("i", 1)
    assert q == {"i": {"$lte": 1}}


async def test_ne():
    q = A.i != 1
    assert q == {"i": {"$ne": 1}}

    q = NE(A.i, 1)
    assert q == {"i": {"$ne": 1}}

    q = NE("i", 1)
    assert q == {"i": {"$ne": 1}}


async def test_nin():
    q = NotIn(A.i, [1])
    assert q == {"i": {"$nin": [1]}}

    q = NotIn(A.i, [1])
    assert q == {"i": {"$nin": [1]}}
