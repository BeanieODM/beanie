from tests.odm.models import Sample


async def test_sum(preset_documents, session):
    n = await Sample.find_many(Sample.integer == 1).sum(Sample.increment)

    assert n == 12

    n = await Sample.find_many(Sample.integer == 1).sum(
        Sample.increment, session=session
    )

    assert n == 12


async def test_avg(preset_documents, session):
    n = await Sample.find_many(Sample.integer == 1).avg(Sample.increment)

    assert n == 4
    n = await Sample.find_many(Sample.integer == 1).avg(
        Sample.increment, session=session
    )

    assert n == 4


async def test_max(preset_documents, session):
    n = await Sample.find_many(Sample.integer == 1).max(Sample.increment)

    assert n == 5

    n = await Sample.find_many(Sample.integer == 1).max(
        Sample.increment, session=session
    )

    assert n == 5


async def test_min(preset_documents, session):
    n = await Sample.find_many(Sample.integer == 1).min(Sample.increment)

    assert n == 3

    n = await Sample.find_many(Sample.integer == 1).min(
        Sample.increment, session=session
    )

    assert n == 3
