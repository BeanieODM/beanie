from tests.odm.models import Sample


async def test_replace_one(preset_documents):
    count_1_before = await Sample.find_many(Sample.integer == 1).count()
    count_2_before = await Sample.find_many(Sample.integer == 2).count()

    a_2 = await Sample.find_one(Sample.integer == 2)
    await Sample.find_one(Sample.integer == 1).replace_one(a_2)

    count_1_after = await Sample.find_many(Sample.integer == 1).count()
    count_2_after = await Sample.find_many(Sample.integer == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1


async def test_replace_self(preset_documents):
    count_1_before = await Sample.find_many(Sample.integer == 1).count()
    count_2_before = await Sample.find_many(Sample.integer == 2).count()

    a_1 = await Sample.find_one(Sample.integer == 1)
    a_1.integer = 2
    await a_1.replace()

    count_1_after = await Sample.find_many(Sample.integer == 1).count()
    count_2_after = await Sample.find_many(Sample.integer == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1
