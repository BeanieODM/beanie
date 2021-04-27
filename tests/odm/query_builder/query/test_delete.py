from tests.odm.query_builder.models import A


async def test_delete_many(preset_documents):
    count_before = await A.count()
    count_find = (
        await A.find_many(A.i > 1).find_many(A.b.o_d == None).count()
    )  # noqa
    await A.find_many(A.i > 1).find_many(A.b.o_d == None).delete()  # noqa
    count_after = await A.count()
    assert count_before - count_find == count_after


async def test_delete_all(preset_documents):
    await A.delete_all()
    count_after = await A.count()
    assert count_after == 0


async def test_delete_self(preset_documents):
    count_before = await A.count()
    result = (
        await A.find_many(A.i > 1).find_many(A.b.o_d == None).to_list()
    )  # noqa
    a = result[0]
    await a.delete()
    count_after = await A.count()
    assert count_before == count_after + 1


async def test_delete_one(preset_documents):
    count_before = await A.count()
    await A.find_one(A.i > 1).find_one(A.b.o_d == None).delete()  # noqa
    count_after = await A.count()
    assert count_before == count_after + 1
