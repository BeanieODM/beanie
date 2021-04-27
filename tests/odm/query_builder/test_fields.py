from beanie.odm.query_builder.operators.find.comparsion import In, NotIn
from tests.odm.query_builder.models import A


def test_nesting():
    assert A.id == "_id"

    q = A.find_many(A.i == 1)
    assert q.find_parameters.get_filter_query() == {"i": 1}
    assert A.i == "i"

    q = A.find_many(A.b.i == 1)
    assert q.find_parameters.get_filter_query() == {"b.i": 1}
    assert A.b.i == "b.i"

    q = A.find_many(A.c_d.s == "test")
    assert q.find_parameters.get_filter_query() == {"c_d.s": "test"}
    assert A.c_d.s == "c_d.s"

    q = A.find_many(A.b.o_d == None)  # noqa
    assert q.find_parameters.get_filter_query() == {"b.o_d": None}
    assert A.b.o_d == "b.o_d"

    q = A.find_many(A.b.i == 1).find_many(A.b.c_d.s == "test")
    assert q.find_parameters.get_filter_query() == {
        "$and": [{"b.i": 1}, {"b.c_d.s": "test"}]
    }


def test_eq():
    q = A.find_many(A.i == 1)
    assert q.find_parameters.get_filter_query() == {"i": 1}


def test_gt():
    q = A.find_many(A.i > 1)
    assert q.find_parameters.get_filter_query() == {"i": {"$gt": 1}}


def test_gte():
    q = A.find_many(A.i >= 1)
    assert q.find_parameters.get_filter_query() == {"i": {"$gte": 1}}


def test_in():
    q = A.find_many(In(A.i, [1, 2, 3, 4]))
    assert dict(q.find_parameters.get_filter_query()) == {
        "i": {"$in": [1, 2, 3, 4]}
    }


def test_lt():
    q = A.find_many(A.i < 1)
    assert q.find_parameters.get_filter_query() == {"i": {"$lt": 1}}


def test_lte():
    q = A.find_many(A.i <= 1)
    assert q.find_parameters.get_filter_query() == {"i": {"$lte": 1}}


def test_ne():
    q = A.find_many(A.i != 1)
    assert q.find_parameters.get_filter_query() == {"i": {"$ne": 1}}


def test_nin():
    q = A.find_many(NotIn(A.i, [1, 2, 3, 4]))
    assert dict(q.find_parameters.get_filter_query()) == {
        "i": {"$nin": [1, 2, 3, 4]}
    }
