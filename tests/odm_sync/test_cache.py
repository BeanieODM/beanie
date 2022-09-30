import asyncio
from time import sleep

from tests.odm_sync.models import SyncDocumentTestModel


def test_find_one(documents):
    documents(5)
    doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 1
    ).run()
    SyncDocumentTestModel.find_one(SyncDocumentTestModel.test_int == 1).set(
        {SyncDocumentTestModel.test_str: "NEW_VALUE"}
    ).run()
    new_doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 1
    ).run()
    assert doc == new_doc

    new_doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 1, ignore_cache=True
    ).run()
    assert doc != new_doc

    sleep(10)

    new_doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 1
    ).run()
    assert doc != new_doc


def test_find_many(documents):
    documents(5)
    docs = SyncDocumentTestModel.find(
        SyncDocumentTestModel.test_int > 1
    ).to_list()

    SyncDocumentTestModel.find(SyncDocumentTestModel.test_int > 1).set(
        {SyncDocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_docs = SyncDocumentTestModel.find(
        SyncDocumentTestModel.test_int > 1
    ).to_list()
    assert docs == new_docs

    new_docs = SyncDocumentTestModel.find(
        SyncDocumentTestModel.test_int > 1, ignore_cache=True
    ).to_list()
    assert docs != new_docs

    sleep(10)

    new_docs = SyncDocumentTestModel.find(
        SyncDocumentTestModel.test_int > 1
    ).to_list()
    assert docs != new_docs


def test_aggregation(documents):
    documents(5)
    docs = SyncDocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()

    SyncDocumentTestModel.find(SyncDocumentTestModel.test_int > 1).set(
        {SyncDocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_docs = SyncDocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs == new_docs

    new_docs = SyncDocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        ignore_cache=True,
    ).to_list()
    assert docs != new_docs

    sleep(10)

    new_docs = SyncDocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs != new_docs


def test_capacity(documents):
    documents(10)
    docs = []
    for i in range(10):
        docs.append(
            SyncDocumentTestModel.find_one(
                SyncDocumentTestModel.test_int == i
            ).run()
        )

    SyncDocumentTestModel.find_one(SyncDocumentTestModel.test_int == 1).set(
        {SyncDocumentTestModel.test_str: "NEW_VALUE"}
    ).run()
    SyncDocumentTestModel.find_one(SyncDocumentTestModel.test_int == 9).set(
        {SyncDocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 1
    ).run()
    assert docs[1] != new_doc

    new_doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 9
    ).run()
    assert docs[9] == new_doc
