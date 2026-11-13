import datetime as dt

import pytest

from tests.odm.models import DocumentTestModel


async def test_find_one(documents, time_machine):
    time_machine.move_to(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc))

    await documents(5)

    doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 1)

    await DocumentTestModel.find_one(DocumentTestModel.test_int == 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )

    cached_doc = await DocumentTestModel.find_one(
        DocumentTestModel.test_int == 1
    )
    assert doc == cached_doc

    # Advance time to ensure cache expiration
    time_machine.shift(dt.timedelta(seconds=11))

    refreshed_doc = await DocumentTestModel.find_one(
        DocumentTestModel.test_int == 1
    )
    assert doc != refreshed_doc


async def test_find_many(documents, time_machine):
    time_machine.move_to(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc))

    await documents(5)
    docs = await DocumentTestModel.find(
        DocumentTestModel.test_int > 1
    ).to_list()

    await DocumentTestModel.find(DocumentTestModel.test_int > 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )

    new_docs = await DocumentTestModel.find(
        DocumentTestModel.test_int > 1
    ).to_list()
    assert docs == new_docs

    new_docs = await DocumentTestModel.find(
        DocumentTestModel.test_int > 1, ignore_cache=True
    ).to_list()
    assert docs != new_docs

    # Advance time to ensure cache expiration
    time_machine.shift(dt.timedelta(seconds=11))

    new_docs = await DocumentTestModel.find(
        DocumentTestModel.test_int > 1
    ).to_list()
    assert docs != new_docs


async def test_aggregation(documents, time_machine):
    time_machine.move_to(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc))

    await documents(5)
    docs = await DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()

    await DocumentTestModel.find(DocumentTestModel.test_int > 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )

    new_docs = await DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs == new_docs

    new_docs = await DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        ignore_cache=True,
    ).to_list()
    assert docs != new_docs

    # Advance time to ensure cache expiration
    time_machine.shift(dt.timedelta(seconds=11))

    new_docs = await DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs != new_docs


async def test_capacity(documents):
    await documents(10)
    docs = []
    for i in range(10):
        docs.append(
            await DocumentTestModel.find_one(DocumentTestModel.test_int == i)
        )

    await DocumentTestModel.find_one(DocumentTestModel.test_int == 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )
    await DocumentTestModel.find_one(DocumentTestModel.test_int == 9).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )

    new_doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 1)
    assert docs[1] != new_doc

    new_doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 9)
    assert docs[9] == new_doc


@pytest.mark.parametrize("query_type", ["find", "aggregate"])
@pytest.mark.parametrize("first_length,second_length", [(1, None), (None, 1)])
async def test_to_list_length_does_not_share_cache(
    documents, query_type, first_length, second_length
):
    await documents(5)

    def query():
        if query_type == "find":
            return DocumentTestModel.find_all().sort("test_int")
        return DocumentTestModel.aggregate([{"$sort": {"test_int": 1}}])

    first = await query().to_list(length=first_length)
    second = await query().to_list(length=second_length)

    for result, length in [(first, first_length), (second, second_length)]:
        values = [
            doc.test_int if query_type == "find" else doc["test_int"]
            for doc in result
        ]
        assert values == list(range(5 if length is None else length))
