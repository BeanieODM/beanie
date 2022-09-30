import pytest
from pymongo.errors import DuplicateKeyError

from beanie.odm_sync.fields import PydanticObjectId
from tests.odm_sync.models import SyncDocumentTestModel


def test_insert_one(document_not_inserted):
    result = SyncDocumentTestModel.insert_one(document_not_inserted)
    document = SyncDocumentTestModel.get(result.id)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


def test_insert_many(documents_not_inserted):
    SyncDocumentTestModel.insert_many(documents_not_inserted(10))
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 10


def test_create(document_not_inserted):
    document_not_inserted.insert()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


def test_create_twice(document_not_inserted):
    document_not_inserted.insert()
    with pytest.raises(DuplicateKeyError):
        document_not_inserted.insert()


def test_insert_one_with_session(document_not_inserted, session):
    result = SyncDocumentTestModel.insert_one(
        document_not_inserted, session=session
    )
    document = SyncDocumentTestModel.get(result.id, session=session)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


def test_insert_many_with_session(documents_not_inserted, session):
    SyncDocumentTestModel.insert_many(
        documents_not_inserted(10), session=session
    )
    documents = SyncDocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 10


def test_create_with_session(document_not_inserted, session):
    document_not_inserted.insert(session=session)
    assert isinstance(document_not_inserted.id, PydanticObjectId)
