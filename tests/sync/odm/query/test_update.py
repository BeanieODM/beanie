import asyncio

import pytest

from beanie.odm.operators.update.general import Set, Max
from tests.sync.models import Sample


def test_update_query():
    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .update_query
    )
    assert q == {"$set": {"integer": 10}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}), Set({Sample.optional: None}))
        .update_query
    )
    assert q == {"$max": {"integer": 10}, "$set": {"optional": None}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}), Set({Sample.optional: None}))
        .update_query
    )
    assert q == {"$set": {"optional": None}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Max({Sample.integer: 10}))
        .update(Set({Sample.optional: None}))
        .update_query
    )
    assert q == {"$max": {"integer": 10}, "$set": {"optional": None}}

    q = (
        Sample.find_many(Sample.integer == 1)
        .update(Set({Sample.integer: 10}))
        .update(Set({Sample.optional: None}))
        .update_query
    )
    assert q == {"$set": {"optional": None}}

    with pytest.raises(TypeError):
        Sample.find_many(Sample.integer == 1).update(40).update_query


def test_update_many(preset_documents):
    Sample.find_many(Sample.increment > 4).find_many(
        Sample.nested.optional == None
    ).update(
        Set({Sample.increment: 100})
    ).run()  # noqa
    result = Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


def test_update_many_linked_method(preset_documents):
    Sample.find_many(Sample.increment > 4).find_many(
        Sample.nested.optional == None
    ).update_many(
        Set({Sample.increment: 100})
    ).run()  # noqa
    result = Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


def test_update_all(preset_documents):
    Sample.update_all(Set({Sample.integer: 100})).run()
    result = Sample.find_all().to_list()
    for sample in result:
        assert sample.integer == 100

    Sample.find_all().update(Set({Sample.integer: 101})).run()
    result = Sample.find_all().to_list()
    for sample in result:
        assert sample.integer == 101


def test_update_one(preset_documents):
    Sample.find_one(Sample.integer == 1).update(
        Set({Sample.integer: 100})
    ).run()
    result = Sample.find_many(Sample.integer == 100).to_list()
    assert len(result) == 1
    assert result[0].integer == 100

    Sample.find_one(Sample.integer == 1).update_one(
        Set({Sample.integer: 101})
    ).run()
    result = Sample.find_many(Sample.integer == 101).to_list()
    assert len(result) == 1
    assert result[0].integer == 101


def test_update_self(preset_documents):
    sample = Sample.find_one(Sample.integer == 1).run()
    sample.update(Set({Sample.integer: 100}))
    assert sample.integer == 100

    result = Sample.find_many(Sample.integer == 100).to_list()
    assert len(result) == 1
    assert result[0].integer == 100


def test_update_many_with_session(preset_documents, session):
    q = (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None)
        .update(Set({Sample.increment: 100}))
        .set_session(session=session)
    )
    assert q.session == session

    q = (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None)
        .update(Set({Sample.increment: 100}), session=session)
        .run()
    )
    # assert q.session == session

    q = (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None, session=session)
        .update(Set({Sample.increment: 100}))
        .run()
    )
    # assert q.session == session

    # q  # noqa
    result = Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


def test_update_many_upsert_with_insert(
    preset_documents, sample_doc_not_saved
):
    Sample.find_many(Sample.integer > 100000).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    ).run()
    asyncio.sleep(2)
    new_docs = Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(new_docs) == 1
    doc = new_docs[0]
    assert doc.integer == sample_doc_not_saved.integer


def test_update_many_upsert_without_insert(
    preset_documents, sample_doc_not_saved
):
    Sample.find_many(Sample.integer > 1).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    ).run()
    asyncio.sleep(2)
    new_docs = Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(new_docs) == 0


def test_update_one_upsert_with_insert(preset_documents, sample_doc_not_saved):
    Sample.find_one(Sample.integer > 100000).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    ).run()
    asyncio.sleep(2)
    new_docs = Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(new_docs) == 1
    doc = new_docs[0]
    assert doc.integer == sample_doc_not_saved.integer


def test_update_one_upsert_without_insert(
    preset_documents, sample_doc_not_saved
):
    Sample.find_one(Sample.integer > 1).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    ).run()
    asyncio.sleep(2)
    new_docs = Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(new_docs) == 0


def test_update_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        Sample.find_many(Sample.increment > 4).update(
            Set({Sample.increment: 100}), wrong="integer_1"
        ).run()

    Sample.find_many(Sample.increment > 4).update(
        Set({Sample.increment: 100}), hint="integer_1"
    ).run()

    Sample.find_one(Sample.increment > 4).update(
        Set({Sample.increment: 100}), hint="integer_1"
    ).run()
