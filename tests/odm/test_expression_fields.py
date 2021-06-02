from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import In, NotIn
from tests.odm.models import Sample


def test_nesting():
    assert Sample.id == "_id"

    q = Sample.find_many(Sample.integer == 1)
    assert q.get_filter_query() == {"integer": 1}
    assert Sample.integer == "integer"

    q = Sample.find_many(Sample.nested.integer == 1)
    assert q.get_filter_query() == {"nested.integer": 1}
    assert Sample.nested.integer == "nested.integer"

    q = Sample.find_many(Sample.union.s == "test")
    assert q.get_filter_query() == {"union.s": "test"}
    assert Sample.union.s == "union.s"

    q = Sample.find_many(Sample.nested.optional == None)  # noqa
    assert q.get_filter_query() == {"nested.optional": None}
    assert Sample.nested.optional == "nested.optional"

    q = Sample.find_many(Sample.nested.integer == 1).find_many(
        Sample.nested.union.s == "test"
    )
    assert q.get_filter_query() == {
        "$and": [{"nested.integer": 1}, {"nested.union.s": "test"}]
    }


def test_eq():
    q = Sample.find_many(Sample.integer == 1)
    assert q.get_filter_query() == {"integer": 1}


def test_gt():
    q = Sample.find_many(Sample.integer > 1)
    assert q.get_filter_query() == {"integer": {"$gt": 1}}


def test_gte():
    q = Sample.find_many(Sample.integer >= 1)
    assert q.get_filter_query() == {"integer": {"$gte": 1}}


def test_in():
    q = Sample.find_many(In(Sample.integer, [1, 2, 3, 4]))
    assert dict(q.get_filter_query()) == {"integer": {"$in": [1, 2, 3, 4]}}


def test_lt():
    q = Sample.find_many(Sample.integer < 1)
    assert q.get_filter_query() == {"integer": {"$lt": 1}}


def test_lte():
    q = Sample.find_many(Sample.integer <= 1)
    assert q.get_filter_query() == {"integer": {"$lte": 1}}


def test_ne():
    q = Sample.find_many(Sample.integer != 1)
    assert q.get_filter_query() == {"integer": {"$ne": 1}}


def test_nin():
    q = Sample.find_many(NotIn(Sample.integer, [1, 2, 3, 4]))
    assert dict(q.get_filter_query()) == {"integer": {"$nin": [1, 2, 3, 4]}}


def test_pos():
    q = +Sample.integer
    assert q == ("integer", SortDirection.ASCENDING)


def test_neg():
    q = -Sample.integer
    assert q == ("integer", SortDirection.DESCENDING)
