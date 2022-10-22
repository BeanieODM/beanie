from time import sleep

from tests.sync.models import DocumentTestModel


def test_find_one(documents):
    documents(5)
    doc = DocumentTestModel.find_one(DocumentTestModel.test_int == 1).run()
    DocumentTestModel.find_one(DocumentTestModel.test_int == 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    ).run()
    new_doc = DocumentTestModel.find_one(DocumentTestModel.test_int == 1).run()
    assert doc == new_doc

    new_doc = DocumentTestModel.find_one(
        DocumentTestModel.test_int == 1, ignore_cache=True
    ).run()
    assert doc != new_doc

    sleep(10)

    new_doc = DocumentTestModel.find_one(DocumentTestModel.test_int == 1).run()
    assert doc != new_doc


def test_find_many(documents):
    documents(5)
    docs = DocumentTestModel.find(DocumentTestModel.test_int > 1).to_list()

    DocumentTestModel.find(DocumentTestModel.test_int > 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_docs = DocumentTestModel.find(DocumentTestModel.test_int > 1).to_list()
    assert docs == new_docs

    new_docs = DocumentTestModel.find(
        DocumentTestModel.test_int > 1, ignore_cache=True
    ).to_list()
    assert docs != new_docs

    sleep(10)

    new_docs = DocumentTestModel.find(DocumentTestModel.test_int > 1).to_list()
    assert docs != new_docs


def test_aggregation(documents):
    documents(5)
    docs = DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()

    DocumentTestModel.find(DocumentTestModel.test_int > 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_docs = DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs == new_docs

    new_docs = DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        ignore_cache=True,
    ).to_list()
    assert docs != new_docs

    sleep(10)

    new_docs = DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
    assert docs != new_docs


def test_capacity(documents):
    documents(10)
    docs = []
    for i in range(10):
        docs.append(
            DocumentTestModel.find_one(DocumentTestModel.test_int == i).run()
        )

    DocumentTestModel.find_one(DocumentTestModel.test_int == 1).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    ).run()
    DocumentTestModel.find_one(DocumentTestModel.test_int == 9).set(
        {DocumentTestModel.test_str: "NEW_VALUE"}
    ).run()

    new_doc = DocumentTestModel.find_one(DocumentTestModel.test_int == 1).run()
    assert docs[1] != new_doc

    new_doc = DocumentTestModel.find_one(DocumentTestModel.test_int == 9).run()
    assert docs[9] == new_doc
