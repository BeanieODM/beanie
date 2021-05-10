import pytest

from beanie.exceptions import DocumentAlreadyCreated
from beanie.odm.fields import PydanticObjectId
from tests.odm.models import DocumentTestModel


async def test_insert_one(document_not_inserted):
    result = await DocumentTestModel.insert_one(document_not_inserted)
    document = await DocumentTestModel.get(result.inserted_id)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


async def test_insert_many(documents_not_inserted):
    await DocumentTestModel.insert_many(documents_not_inserted(10))
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 10


async def test_create(document_not_inserted):
    await document_not_inserted.insert()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


async def test_create_twice(document_not_inserted):
    await document_not_inserted.insert()
    with pytest.raises(DocumentAlreadyCreated):
        await document_not_inserted.insert()


async def test_insert_one_with_session(document_not_inserted, session):
    result = await DocumentTestModel.insert_one(
        document_not_inserted, session=session
    )
    document = await DocumentTestModel.get(result.inserted_id, session=session)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


async def test_insert_many_with_session(documents_not_inserted, session):
    await DocumentTestModel.insert_many(
        documents_not_inserted(10), session=session
    )
    documents = await DocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 10


async def test_create_with_session(document_not_inserted, session):
    await document_not_inserted.insert(session=session)
    assert isinstance(document_not_inserted.id, PydanticObjectId)
