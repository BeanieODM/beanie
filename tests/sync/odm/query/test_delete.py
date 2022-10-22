import pytest
from tests.sync.models import Sample


def test_delete_many(preset_documents):
    count_before = Sample.count()
    count_find = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .count()
    )  # noqa
    delete_result = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .delete()
        .run()
    )  # noqa
    count_deleted = delete_result.deleted_count
    count_after = Sample.count()
    assert count_before - count_find == count_after
    assert count_after + count_deleted == count_before
    # assert isinstance(
    #     Sample.find_many(Sample.integer > 1)
    #     .find_many(Sample.nested.optional == None)
    #     .delete_many(),
    #     DeleteMany,
    # )# noqa


def test_delete_all(preset_documents):
    count_before = Sample.count()
    delete_result = Sample.delete_all()
    count_deleted = delete_result.deleted_count
    count_after = Sample.count()
    assert count_after == 0
    assert count_after + count_deleted == count_before


def test_delete_self(preset_documents):
    count_before = Sample.count()
    result = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .to_list()
    )  # noqa
    a = result[0]
    delete_result = a.delete()
    count_deleted = delete_result.deleted_count
    count_after = Sample.count()
    assert count_before == count_after + 1
    assert count_deleted == 1


def test_delete_one(preset_documents):
    count_before = Sample.count()
    delete_result = (
        Sample.find_one(Sample.integer > 1)
        .find_one(Sample.nested.optional == None)
        .delete()
        .run()
    )  # noqa
    count_after = Sample.count()
    count_deleted = delete_result.deleted_count
    assert count_before == count_after + 1
    assert count_deleted == 1

    count_before = Sample.count()
    delete_result = (
        Sample.find_one(Sample.integer > 1)
        .find_one(Sample.nested.optional == None)
        .delete_one()
        .run()
    )  # noqa
    count_deleted = delete_result.deleted_count
    count_after = Sample.count()
    assert count_before == count_after + 1
    assert count_deleted == 1


def test_delete_many_with_session(preset_documents, session):
    count_before = Sample.count()
    count_find = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .count()
    )  # noqa
    q = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .set_session(session=session)
        .delete()
        .run()
    )  # noqa

    # assert q.session == session

    delete_result = q
    count_deleted = delete_result.deleted_count
    count_after = Sample.count()
    assert count_before - count_find == count_after
    assert count_after + count_deleted == count_before


def test_delete_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        Sample.find_many(Sample.increment > 4).delete(wrong="integer_1").run()

    delete_result = (
        Sample.find_many(Sample.increment > 4).delete(hint="integer_1").run()
    )
    assert delete_result is not None

    delete_result = (
        Sample.find_one(Sample.increment > 4).delete(hint="integer_1").run()
    )
    assert delete_result is not None
