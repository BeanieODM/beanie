import pytest

from beanie.exceptions import DocumentAlreadyCreated
from beanie.fields import PydanticObjectId
from tests.models import DocumentTestModel


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
    await document_not_inserted.create()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


async def test_create_twice(document_not_inserted):
    await document_not_inserted.create()
    with pytest.raises(DocumentAlreadyCreated):
        await document_not_inserted.create()
