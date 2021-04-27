from beanie.odm.query_builder.operators.update.general import Max, Set
from beanie.odm.query_builder.queries.update import UpdateQuery, UpdateMany
from tests.odm.query_builder.models import A


async def test_set():
    q = A.find_many(A.i == 1).set({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 100}}

    q = A.find_many(A.i == 1).update(Max({A.i: 10})).set({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"i": 10}, "$set": {"i": 100}}


async def test_current_date():
    q = A.find_many(A.i == 1).current_date({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$currentDate": {"i": 100}}

    q = A.find_many(A.i == 1).update(Max({A.i: 10})).current_date({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"i": 10}, "$currentDate": {"i": 100}}


async def test_inc():
    q = A.find_many(A.i == 1).inc({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$inc": {"i": 100}}

    q = A.find_many(A.i == 1).update(Max({A.i: 10})).inc({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"i": 10}, "$inc": {"i": 100}}


async def test_min():
    q = A.find_many(A.i == 1).min({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$min": {"i": 100}}

    q = A.find_many(A.i == 1).update(Max({A.i: 10})).min({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"i": 10}, "$min": {"i": 100}}


async def test_max():
    q = A.find_many(A.i == 1).max({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"i": 100}}

    q = A.find_many(A.i == 1).update(Set({A.i: 10})).max({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 10}, "$max": {"i": 100}}


async def test_mul():
    q = A.find_many(A.i == 1).mul({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$mul": {"i": 100}}

    q = A.find_many(A.i == 1).update(Set({A.i: 10})).mul({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 10}, "$mul": {"i": 100}}


async def test_rename():
    q = A.find_many(A.i == 1).rename({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$rename": {"i": 100}}

    q = A.find_many(A.i == 1).update(Set({A.i: 10})).rename({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 10}, "$rename": {"i": 100}}


async def test_set_on_insert():
    q = A.find_many(A.i == 1).set_on_insert({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$setOnInsert": {"i": 100}}

    q = A.find_many(A.i == 1).update(Set({A.i: 10})).set_on_insert({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 10}, "$setOnInsert": {"i": 100}}


async def test_unset():
    q = A.find_many(A.i == 1).unset({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$unset": {"i": 100}}

    q = A.find_many(A.i == 1).update(Set({A.i: 10})).unset({A.i: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"i": 10}, "$unset": {"i": 100}}
