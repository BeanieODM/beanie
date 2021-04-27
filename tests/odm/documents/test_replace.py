from tests.odm.query_builder.models import A


async def test_replace_one(preset_documents):
    count_1_before = await A.find_many(A.i == 1).count()
    count_2_before = await A.find_many(A.i == 2).count()

    a_2 = await A.find_one(A.i == 2)
    await A.find_one(A.i == 1).replace_one(a_2)

    count_1_after = await A.find_many(A.i == 1).count()
    count_2_after = await A.find_many(A.i == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1


async def test_replace_self(preset_documents):
    count_1_before = await A.find_many(A.i == 1).count()
    count_2_before = await A.find_many(A.i == 2).count()

    a_1 = await A.find_one(A.i == 1)
    a_1.i = 2
    await a_1.replace()

    count_1_after = await A.find_many(A.i == 1).count()
    count_2_after = await A.find_many(A.i == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1
