import pymongo

from beanie.odm.fields import PydanticObjectId
from tests.sync.models import DocumentTestModel


def test_get(document):
    new_document = DocumentTestModel.get(document.id).run()
    assert new_document == document


def test_get_not_found(document):
    new_document = DocumentTestModel.get(PydanticObjectId()).run()
    assert new_document is None


def test_find_one(documents):
    inserted_one = documents(1, "kipasa")
    documents(10, "smthe else")
    expected_doc_id = PydanticObjectId(inserted_one[0])
    new_document = DocumentTestModel.find_one({"test_str": "kipasa"}).run()
    assert new_document.id == expected_doc_id


def test_find_one_not_found(documents):
    documents(10, "smthe else")

    new_document = DocumentTestModel.find_one({"test_str": "wrong"}).run()
    assert new_document is None


def test_find_one_more_than_one_found(documents):
    documents(10, "one")
    documents(10, "two")
    new_document = DocumentTestModel.find_one({"test_str": "one"}).run()
    assert new_document.test_str == "one"


def test_find_all(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_all().to_list()
    assert len(result) == 7


def test_find_all_limit(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_all(limit=5).to_list()
    assert len(result) == 5


def test_find_all_skip(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_all(skip=1).to_list()
    assert len(result) == 6


def test_find_all_sort(documents):
    documents(4, "uno", True)
    documents(2, "dos", True)
    documents(1, "cuatro", True)
    result = DocumentTestModel.find_all(
        sort=[
            ("test_str", pymongo.ASCENDING),
            ("test_int", pymongo.DESCENDING),
        ]
    ).to_list()
    assert result[0].test_str == "cuatro"
    assert result[1].test_str == result[2].test_str == "dos"
    assert (
        result[3].test_str
        == result[4].test_str
        == result[5].test_str
        == result[5].test_str
        == "uno"
    )

    assert result[1].test_int >= result[2].test_int
    assert (
        result[3].test_int
        >= result[4].test_int
        >= result[5].test_int
        >= result[6].test_int
    )


def test_find_many(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_many(
        DocumentTestModel.test_str == "uno"
    ).to_list()
    assert len(result) == 4


def test_find_many_limit(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_many(
        {"test_str": "uno"}, limit=2
    ).to_list()
    assert len(result) == 2


def test_find_many_skip(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_many({"test_str": "uno"}, skip=1).to_list()
    assert len(result) == 3


def test_find_many_sort(documents):
    documents(4, "uno", True)
    documents(2, "dos", True)
    documents(1, "cuatro", True)
    result = DocumentTestModel.find_many(
        {"test_str": "uno"}, sort="test_int"
    ).to_list()
    assert (
        result[0].test_int
        <= result[1].test_int
        <= result[2].test_int
        <= result[3].test_int
    )

    result = DocumentTestModel.find_many(
        {"test_str": "uno"}, sort=[("test_int", pymongo.DESCENDING)]
    ).to_list()
    assert (
        result[0].test_int
        >= result[1].test_int
        >= result[2].test_int
        >= result[3].test_int
    )


def test_find_many_not_found(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_many({"test_str": "wrong"}).to_list()
    assert len(result) == 0


def test_get_with_session(document, session):
    new_document = DocumentTestModel.get(document.id, session=session).run()
    assert new_document == document


def test_find_one_with_session(documents, session):
    inserted_one = documents(1, "kipasa")
    documents(10, "smthe else")

    expected_doc_id = PydanticObjectId(inserted_one[0])

    new_document = DocumentTestModel.find_one(
        {"test_str": "kipasa"}, session=session
    ).run()
    assert new_document.id == expected_doc_id


def test_find_all_with_session(documents, session):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_all(session=session).to_list()
    assert len(result) == 7


def test_find_many_with_session(documents, session):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    result = DocumentTestModel.find_many(
        {"test_str": "uno"}, session=session
    ).to_list()
    assert len(result) == 4
