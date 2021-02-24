import pytest
from pydantic import BaseModel, Field

from beanie import Document
from beanie.exceptions import DocumentAlreadyCreated, DocumentWasNotSaved
from beanie.fields import PydanticObjectId
from tests.models import DocumentTestModel, SubDocument


async def test_init():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(AttributeError):
        NewDocument(test_str="test")


async def test_save(document_not_inserted):
    await document_not_inserted.create()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


async def test_save_twice(document_not_inserted):
    await document_not_inserted.create()
    with pytest.raises(DocumentAlreadyCreated):
        await document_not_inserted.create()


async def test_replace(document):
    document.test_str = "REPLACED_VALUE"
    await document.replace()
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_str == "REPLACED_VALUE"


async def test_replace_not_saved(document_not_inserted):
    with pytest.raises(DocumentWasNotSaved):
        await document_not_inserted.replace()


async def test_delete(document):
    doc_id = document.id
    await document.delete()
    new_document = await DocumentTestModel.get(doc_id)
    assert new_document is None


async def test_update_without_filter_query(document):
    buf_len = len(document.test_list)
    to_insert = SubDocument(test_str="test")
    await document.update(
        update_query={"$push": {"test_list": to_insert.dict()}}
    )
    new_document = await DocumentTestModel.get(document.id)
    assert len(new_document.test_list) == buf_len + 1


async def test_update_with_filter_query(document):
    await document.update(
        update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
        filter_query={"_id": document.id, "test_list.test_str": "foo"},
    )
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_list[0].test_str == "foo_foo"


async def test_get(document):
    new_document = await DocumentTestModel.get(document.id)
    assert new_document == document


async def test_get_not_found(document):
    new_document = await DocumentTestModel.get(PydanticObjectId())
    assert new_document is None


async def test_find_one(document):
    new_document = await DocumentTestModel.find_one({"test_str": "kipasa"})
    assert new_document == document


async def test_find_one_not_found(document):
    new_document = await DocumentTestModel.find_one({"test_str": "wrong"})
    assert new_document is None


async def test_find_one_more_than_one_found(document_not_inserted, collection):
    for s in ["one", "one", "three"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    new_document = await DocumentTestModel.find_one({"test_str": "one"})
    assert new_document.test_str == "one"


async def test_all(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = []
    async for document in DocumentTestModel.all():
        result.append(document)
    assert len(result) == 7


async def test_find(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = []
    async for document in DocumentTestModel.find({"test_str": "uno"}):
        result.append(document)
    assert len(result) == 4


async def test_find_not_found(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = []
    async for document in DocumentTestModel.find({"test_str": "wrong"}):
        result.append(document)
    assert len(result) == 0


async def test_aggregate(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = []
    async for aggregation in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ):
        result.append(aggregation)
    assert len(result) == 3
    assert {"_id": "cuatro", "total": 42} in result
    assert {"_id": "dos", "total": 84} in result
    assert {"_id": "uno", "total": 168} in result


async def test_aggregate_with_item_model(collection, document_not_inserted):
    class OutputItem(BaseModel):
        id: str = Field(None, alias="_id")
        total: int

    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    ids = []
    async for i in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputItem,
    ):
        if i.id == "cuatro":
            assert i.total == 42

        elif i.id == "dos":
            assert i.total == 84
        elif i.id == "uno":
            assert i.total == 168
        else:
            raise KeyError
        ids.append(i.id)
    assert set(ids) == {"cuatro", "dos", "uno"}


async def test_delete_many(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await DocumentTestModel.delete_many({"test_str": "uno"})
    documents = await DocumentTestModel.all().to_list()
    assert len(documents) == 3


async def test_delete_many_not_found(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await DocumentTestModel.delete_many({"test_str": "wrong"})
    documents = await DocumentTestModel.all().to_list()
    assert len(documents) == 7


async def test_delete_all(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await DocumentTestModel.delete_all()
    documents = await DocumentTestModel.all().to_list()
    assert len(documents) == 0
