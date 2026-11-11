import datetime as dt
from unittest.mock import patch

import pytest

from beanie import BulkWriter
from beanie.odm.operators.update.general import Max, Set
from beanie.odm.queries.update import UpdateOnePyMongo, UpdateResponse
from tests.odm.models import Sample


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


async def test_update_many(preset_documents):
    await (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None)
        .update(Set({Sample.increment: 100}))
    )
    result = await Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


async def test_update_many_linked_method(preset_documents):
    await (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None)
        .update_many(Set({Sample.increment: 100}))
    )
    result = await Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


async def test_update_all(preset_documents):
    await Sample.update_all(Set({Sample.integer: 100}))
    result = await Sample.find_all().to_list()
    for sample in result:
        assert sample.integer == 100

    await Sample.find_all().update(Set({Sample.integer: 101}))
    result = await Sample.find_all().to_list()
    for sample in result:
        assert sample.integer == 101


async def test_update_one(preset_documents):
    await Sample.find_one(Sample.integer == 1).update(
        Set({Sample.integer: 100})
    )
    result = await Sample.find_many(Sample.integer == 100).to_list()
    assert len(result) == 1
    assert result[0].integer == 100

    await Sample.find_one(Sample.integer == 1).update_one(
        Set({Sample.integer: 101})
    )
    result = await Sample.find_many(Sample.integer == 101).to_list()
    assert len(result) == 1
    assert result[0].integer == 101


@pytest.mark.parametrize(
    "response_type", [UpdateResponse.OLD_DOCUMENT, UpdateResponse.NEW_DOCUMENT]
)
@pytest.mark.parametrize("operation", ["update", "upsert"])
async def test_update_one_preserves_find_sort(
    preset_documents, sample_doc_not_saved, response_type, operation
):
    query = Sample.find_one(sort=[("increment", -1)])
    expected = await query
    updater = getattr(query, operation)
    kwargs = (
        {"on_insert": sample_doc_not_saved} if operation == "upsert" else {}
    )
    updated = await updater(
        Set({Sample.integer: 100}), response_type=response_type, **kwargs
    )
    assert updated.id == expected.id
    stored = await Sample.get(expected.id, ignore_cache=True)
    assert stored.integer == 100


@pytest.mark.parametrize("operation", ["update", "upsert"])
@pytest.mark.parametrize("use_bulk", [False, True])
async def test_update_one_find_sort_not_passed_to_update_result(
    preset_documents, sample_doc_not_saved, operation, use_bulk
):
    updater = getattr(Sample.find_one(sort=[("increment", -1)]), operation)
    kwargs = (
        {"on_insert": sample_doc_not_saved} if operation == "upsert" else {}
    )
    if use_bulk:
        kwargs.update(
            bulk_writer=BulkWriter(), response_type=UpdateResponse.NEW_DOCUMENT
        )
    query = updater(Set({Sample.integer: 100}), **kwargs)
    if use_bulk:
        with patch(
            "beanie.odm.queries.update.UpdateOnePyMongo",
            wraps=UpdateOnePyMongo,
        ) as update_one:
            await query
            update_one.assert_called_once()
            assert "sort" not in update_one.call_args.kwargs
    else:
        collection = Sample.get_pymongo_collection()
        with patch.object(
            collection, "update_one", wraps=collection.update_one
        ) as update_one:
            await query
            update_one.assert_awaited_once()
            assert "sort" not in update_one.await_args.kwargs


@pytest.mark.parametrize(
    "initial_response",
    [UpdateResponse.NEW_DOCUMENT, UpdateResponse.UPDATE_RESULT],
)
async def test_update_one_find_sort_follows_final_response(
    preset_documents, initial_response
):
    query = Sample.find_one(sort=[("increment", -1)]).update(
        Set({Sample.integer: 100}), response_type=initial_response
    )
    final_response = (
        UpdateResponse.NEW_DOCUMENT
        if initial_response is UpdateResponse.UPDATE_RESULT
        else UpdateResponse.UPDATE_RESULT
    )
    query.update(response_type=final_response)
    collection = Sample.get_pymongo_collection()
    method = (
        "find_one_and_update"
        if final_response is UpdateResponse.NEW_DOCUMENT
        else "update_one"
    )
    with patch.object(
        collection, method, wraps=getattr(collection, method)
    ) as update_one:
        result = await query
        update_one.assert_awaited_once()
        if final_response is UpdateResponse.NEW_DOCUMENT:
            assert result.increment == 9
            assert update_one.await_args.kwargs["sort"] == [("increment", -1)]
        else:
            assert result.modified_count == 1
            assert "sort" not in update_one.await_args.kwargs


@pytest.mark.parametrize("sort", [None, []])
async def test_update_one_without_find_sort(preset_documents, sort):
    query = Sample.find_one(sort=sort)
    expected = await query
    updated = await query.update(
        Set({Sample.integer: 100}), response_type=UpdateResponse.NEW_DOCUMENT
    )
    assert updated.id == expected.id


async def test_update_one_explicit_sort_overrides_find(preset_documents):
    query = Sample.find_one(sort=[("increment", -1)])
    expected = await Sample.find_one(sort=[("increment", 1)])
    updated = await query.update(
        Set({Sample.integer: 100}),
        response_type=UpdateResponse.NEW_DOCUMENT,
        sort=[("increment", 1)],
    )
    assert updated.id == expected.id


async def test_update_self(preset_documents):
    sample = await Sample.find_one(Sample.integer == 1)
    await sample.update(Set({Sample.integer: 100}))
    assert sample.integer == 100

    result = await Sample.find_many(Sample.integer == 100).to_list()
    assert len(result) == 1
    assert result[0].integer == 100


async def test_update_many_with_session(preset_documents, session):
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
    )
    assert q.session == session

    q = (
        Sample.find_many(Sample.increment > 4)
        .find_many(Sample.nested.optional == None, session=session)
        .update(Set({Sample.increment: 100}))
    )
    assert q.session == session

    await q
    result = await Sample.find_many(Sample.increment == 100).to_list()
    assert len(result) == 3
    for sample in result:
        assert sample.increment == 100


async def test_update_many_upsert_with_insert(
    preset_documents, sample_doc_not_saved, time_machine
):
    time_machine.move_to(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc))

    await Sample.find_many(Sample.integer > 100000).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    )

    # Advance time to ensure eventual consistency/cache expiration
    time_machine.shift(dt.timedelta(seconds=11))

    docs = await Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(docs) == 1
    doc = docs[0]
    assert doc.integer == sample_doc_not_saved.integer


async def test_update_many_upsert_without_insert(
    preset_documents, sample_doc_not_saved, time_machine
):
    time_machine.move_to(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc))

    await Sample.find_many(Sample.integer > 1).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    )

    # Advance time to ensure eventual consistency/cache expiration
    time_machine.shift(dt.timedelta(seconds=11))

    docs = await Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(docs) == 0


async def test_update_one_upsert_with_insert(
    preset_documents, sample_doc_not_saved
):
    await Sample.find_one(Sample.integer > 100000).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    )
    docs = await Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(docs) == 1
    doc = docs[0]
    assert doc.integer == sample_doc_not_saved.integer


async def test_update_one_upsert_without_insert(
    preset_documents, sample_doc_not_saved
):
    await Sample.find_one(Sample.integer > 1).upsert(
        Set({Sample.integer: 100}), on_insert=sample_doc_not_saved
    )
    docs = await Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(docs) == 0


async def test_update_one_upsert_without_insert_return_doc(
    preset_documents, sample_doc_not_saved
):
    result = await Sample.find_one(Sample.integer > 1).upsert(
        Set({Sample.integer: 100}),
        on_insert=sample_doc_not_saved,
        response_type=UpdateResponse.NEW_DOCUMENT,
    )
    assert isinstance(result, Sample)

    docs = await Sample.find_many(
        Sample.string == sample_doc_not_saved.string
    ).to_list()
    assert len(docs) == 0


async def test_update_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        await Sample.find_many(Sample.increment > 4).update(
            Set({Sample.increment: 100}), wrong="integer_1"
        )

    await Sample.find_many(Sample.increment > 4).update(
        Set({Sample.increment: 100}), hint="integer_1"
    )

    await Sample.find_one(Sample.increment > 4).update(
        Set({Sample.increment: 100}), hint="integer_1"
    )


def test_clone():
    q = Sample.find_many(Sample.integer == 1).update(Set({Sample.integer: 10}))
    new_q = q.clone()
    new_q.update(Max({Sample.integer: 10}))
    assert q.update_query == {"$set": {"integer": 10}}
    assert new_q.update_query == {
        "$max": {"integer": 10},
        "$set": {"integer": 10},
    }
