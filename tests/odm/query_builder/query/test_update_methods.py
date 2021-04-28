from beanie.odm.query_builder.operators.update.general import Max, Set
from beanie.odm.query_builder.queries.update import UpdateQuery, UpdateMany
from tests.odm.query_builder.models import Sample


async def test_set():
    q = Sample.find_many(Sample.integer == 1).set({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$set": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}))
        .set({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$max": {"integer": 10},
        "$set": {"integer": 100},
    }


async def test_current_date():
    q = Sample.find_many(Sample.integer == 1).current_date(
        {Sample.integer: 100}
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$currentDate": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}))
        .current_date({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$max": {"integer": 10},
        "$currentDate": {"integer": 100},
    }


async def test_inc():
    q = Sample.find_many(Sample.integer == 1).inc({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$inc": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}))
        .inc({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$max": {"integer": 10},
        "$inc": {"integer": 100},
    }


async def test_min():
    q = Sample.find_many(Sample.integer == 1).min({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$min": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}))
        .min({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$max": {"integer": 10},
        "$min": {"integer": 100},
    }


async def test_max():
    q = Sample.find_many(Sample.integer == 1).max({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$max": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .max({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$set": {"integer": 10},
        "$max": {"integer": 100},
    }


async def test_mul():
    q = Sample.find_many(Sample.integer == 1).mul({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$mul": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .mul({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$set": {"integer": 10},
        "$mul": {"integer": 100},
    }


async def test_rename():
    q = Sample.find_many(Sample.integer == 1).rename({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$rename": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .rename({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$set": {"integer": 10},
        "$rename": {"integer": 100},
    }


async def test_set_on_insert():
    q = Sample.find_many(Sample.integer == 1).set_on_insert(
        {Sample.integer: 100}
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$setOnInsert": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .set_on_insert({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$set": {"integer": 10},
        "$setOnInsert": {"integer": 100},
    }


async def test_unset():
    q = Sample.find_many(Sample.integer == 1).unset({Sample.integer: 100})

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {"$unset": {"integer": 100}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .unset({Sample.integer: 100})
    )

    assert isinstance(q, UpdateQuery)
    assert isinstance(q, UpdateMany)

    assert q.update_query == {
        "$set": {"integer": 10},
        "$unset": {"integer": 100},
    }
