from tests.sync.models import Sample


def test_sum(preset_documents, session):
    n = Sample.find_many(Sample.integer == 1).sum(Sample.increment)

    assert n == 12

    n = Sample.find_many(Sample.integer == 1).sum(
        Sample.increment, session=session
    )

    assert n == 12


def test_sum_without_docs(session):
    n = Sample.find_many(Sample.integer == 1).sum(Sample.increment)

    assert n is None

    n = Sample.find_many(Sample.integer == 1).sum(
        Sample.increment, session=session
    )

    assert n is None


def test_avg(preset_documents, session):
    n = Sample.find_many(Sample.integer == 1).avg(Sample.increment)

    assert n == 4
    n = Sample.find_many(Sample.integer == 1).avg(
        Sample.increment, session=session
    )

    assert n == 4


def test_avg_without_docs(session):
    n = Sample.find_many(Sample.integer == 1).avg(Sample.increment)

    assert n is None
    n = Sample.find_many(Sample.integer == 1).avg(
        Sample.increment, session=session
    )

    assert n is None


def test_max(preset_documents, session):
    n = Sample.find_many(Sample.integer == 1).max(Sample.increment)

    assert n == 5

    n = Sample.find_many(Sample.integer == 1).max(
        Sample.increment, session=session
    )

    assert n == 5


def test_max_without_docs(session):
    n = Sample.find_many(Sample.integer == 1).max(Sample.increment)

    assert n is None

    n = Sample.find_many(Sample.integer == 1).max(
        Sample.increment, session=session
    )

    assert n is None


def test_min(preset_documents, session):
    n = Sample.find_many(Sample.integer == 1).min(Sample.increment)

    assert n == 3

    n = Sample.find_many(Sample.integer == 1).min(
        Sample.increment, session=session
    )

    assert n == 3


def test_min_without_docs(session):
    n = Sample.find_many(Sample.integer == 1).min(Sample.increment)

    assert n is None

    n = Sample.find_many(Sample.integer == 1).min(
        Sample.increment, session=session
    )

    assert n is None
