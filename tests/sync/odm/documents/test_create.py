import pytest
from pymongo.errors import DuplicateKeyError

from beanie.odm.fields import PydanticObjectId
from tests.sync.models import DocumentTestModel


def test_insert_one(document_not_inserted):
    result = DocumentTestModel.insert_one(document_not_inserted)
    document = DocumentTestModel.get(result.id).run()
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


def test_insert_many(documents_not_inserted):
    DocumentTestModel.insert_many(documents_not_inserted(10))
    documents = DocumentTestModel.find_all().to_list()
    assert len(documents) == 10


def test_create(document_not_inserted):
    document_not_inserted.insert()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


def test_create_twice(document_not_inserted):
    document_not_inserted.insert()
    with pytest.raises(DuplicateKeyError):
        document_not_inserted.insert()


def test_insert_one_with_session(document_not_inserted, session):
    result = DocumentTestModel.insert_one(
        document_not_inserted, session=session
    )
    document = DocumentTestModel.get(result.id, session=session).run()
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


def test_insert_many_with_session(documents_not_inserted, session):
    DocumentTestModel.insert_many(documents_not_inserted(10), session=session)
    documents = DocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 10


def test_create_with_session(document_not_inserted, session):
    document_not_inserted.insert(session=session)
    assert isinstance(document_not_inserted.id, PydanticObjectId)
