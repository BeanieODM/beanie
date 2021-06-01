from beanie.odm.operators.find.comparison import (
    Eq,
    GT,
    GTE,
    In,
    LT,
    LTE,
    NE,
    NotIn,
)
from tests.odm.models import Sample


async def test_eq():
    q = Sample.integer == 1
    assert q == {"integer": 1}

    q = Eq(Sample.integer, 1)
    assert q == {"integer": 1}

    q = Eq("integer", 1)
    assert q == {"integer": 1}


async def test_gt():
    q = Sample.integer > 1
    assert q == {"integer": {"$gt": 1}}

    q = GT(Sample.integer, 1)
    assert q == {"integer": {"$gt": 1}}

    q = GT("integer", 1)
    assert q == {"integer": {"$gt": 1}}


async def test_gte():
    q = Sample.integer >= 1
    assert q == {"integer": {"$gte": 1}}

    q = GTE(Sample.integer, 1)
    assert q == {"integer": {"$gte": 1}}

    q = GTE("integer", 1)
    assert q == {"integer": {"$gte": 1}}


async def test_in():
    q = In(Sample.integer, [1])
    assert q == {"integer": {"$in": [1]}}

    q = In(Sample.integer, [1])
    assert q == {"integer": {"$in": [1]}}


async def test_lt():
    q = Sample.integer < 1
    assert q == {"integer": {"$lt": 1}}

    q = LT(Sample.integer, 1)
    assert q == {"integer": {"$lt": 1}}

    q = LT("integer", 1)
    assert q == {"integer": {"$lt": 1}}


async def test_lte():
    q = Sample.integer <= 1
    assert q == {"integer": {"$lte": 1}}

    q = LTE(Sample.integer, 1)
    assert q == {"integer": {"$lte": 1}}

    q = LTE("integer", 1)
    assert q == {"integer": {"$lte": 1}}


async def test_ne():
    q = Sample.integer != 1
    assert q == {"integer": {"$ne": 1}}

    q = NE(Sample.integer, 1)
    assert q == {"integer": {"$ne": 1}}

    q = NE("integer", 1)
    assert q == {"integer": {"$ne": 1}}


async def test_nin():
    q = NotIn(Sample.integer, [1])
    assert q == {"integer": {"$nin": [1]}}

    q = NotIn(Sample.integer, [1])
    assert q == {"integer": {"$nin": [1]}}
