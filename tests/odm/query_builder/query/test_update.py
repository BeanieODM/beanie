from beanie.odm.query_builder.operators.update.general import Set, Max
from tests.odm.query_builder.models import A


async def test_update_query():
    q = A.find_many(A.i == 1).update(Set({A.i: 10})).update_query
    assert q == {"$set": {"i": 10}}

    q = (
        A.find_many(A.i == 1)
        .update(Max({A.i: 10}), Set({A.o_d: None}))
        .update_query
    )
    assert q == {"$max": {"i": 10}, "$set": {"o_d": None}}

    q = (
        A.find_many(A.i == 1)
        .update(Set({A.i: 10}), Set({A.o_d: None}))
        .update_query
    )
    assert q == {"$set": {"o_d": None}}

    q = (
        A.find_many(A.i == 1)
        .update(Max({A.i: 10}))
        .update(Set({A.o_d: None}))
        .update_query
    )
    assert q == {"$max": {"i": 10}, "$set": {"o_d": None}}

    q = (
        A.find_many(A.i == 1)
        .update(Set({A.i: 10}))
        .update(Set({A.o_d: None}))
        .update_query
    )
    assert q == {"$set": {"o_d": None}}


async def test_update_many(preset_documents):
    await A.find_many(A.i > 1).find_many(A.b.o_d == None).update(
        Set({A.i: 100})
    )  # noqa
    result = await A.find_many(A.i == 100).to_list()
    assert len(result) == 3
    for a in result:
        assert a.i == 100


async def test_update_all(preset_documents):
    await A.update_all(Set({A.i: 100}))
    result = await A.find_all().to_list()
    for a in result:
        assert a.i == 100

    await A.find_all().update(Set({A.i: 101}))
    result = await A.find_all().to_list()
    for a in result:
        assert a.i == 101


async def test_update_one(preset_documents):
    await A.find_one(A.i == 1).update(Set({A.i: 100}))
    result = await A.find_many(A.i == 100).to_list()
    assert len(result) == 1
    assert result[0].i == 100


async def test_update_self(preset_documents):
    a = await A.find_one(A.i == 1)
    await a.update(Set({A.i: 100}))
    assert a.i == 100

    result = await A.find_many(A.i == 100).to_list()
    assert len(result) == 1
    assert result[0].i == 100
