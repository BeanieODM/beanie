import asyncio

from tests.odm.models import DocumentTestModel


async def test_find_one(documents):
    await documents(5)
    doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 1)
    await DocumentTestModel.find_one(DocumentTestModel.test_int == 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    )
    new_doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 1)
    assert doc == new_doc

    new_doc = await DocumentTestModel.find_one(
        DocumentTestModel.test_int == 1, ignore_cache=True
    )
    assert doc != new_doc

    await asyncio.sleep(10)

    new_doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 1)
    assert doc != new_doc


async def test_find_many(documents):
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

    await asyncio.sleep(10)

    new_docs = await DocumentTestModel.find(
        DocumentTestModel.test_int > 1
    ).to_list()
    assert docs != new_docs


async def test_aggregation(documents):
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

    await asyncio.sleep(10)

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
