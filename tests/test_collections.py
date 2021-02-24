import pytest
from pydantic import BaseModel, Field

from beanie.exceptions import DocumentNotFound
from beanie.fields import PydanticObjectId
from tests.models import SubDocument


async def test_insert_one(collection, document_not_inserted, loop):
    document = document_not_inserted
    assert document.id is None
    inserted_document = await collection.insert_one(document)
    assert isinstance(inserted_document.id, PydanticObjectId)


async def test_insert_one_wrong_type(collection):
    with pytest.raises(TypeError):
        await collection.insert_one("wrong_type")


async def test_replace_one(collection, document, loop):
    document.test_int = 14
    await collection.replace_one(document)
    new_document = await collection.get_one(document.id)
    assert document.id == new_document.id
    assert new_document.test_int == 14


async def test_replace_one_no_id(collection, document_not_inserted, loop):
    document = document_not_inserted
    document.test_int = 14
    with pytest.raises(ValueError):
        await collection.replace_one(document)


async def test_replace_one_wrong_id(collection, document, loop):
    document.id = PydanticObjectId()
    with pytest.raises(DocumentNotFound):
        await collection.replace_one(document)


async def test_replace_one_wrong_type(collection):
    with pytest.raises(TypeError):
        await collection.replace_one("wrong_type")


async def test_update_one(collection, document, loop):
    to_insert = SubDocument(test_str="test")
    await collection.update_one(
        document, update_query={"$push": {"test_list": to_insert.dict()}}
    )
    new_document = await collection.get_one(document.id)
    assert len(new_document.test_list) == len(document.test_list) + 1


async def test_update_one_with_search_query(collection, document, loop):
    await collection.update_one(
        document,
        update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
        filter_query={"_id": document.id, "test_list.test_str": "foo"},
    )
    new_document = await collection.get_one(document.id)
    assert new_document.test_list[0].test_str == "foo_foo"


async def test_update_many(collection, document_not_inserted, loop):
    document_not_inserted.test_int = 43
    await collection.insert_one(document_not_inserted)
    document_not_inserted.test_int = 44
    await collection.insert_one(document_not_inserted)
    await collection.update_many(
        update_query={"$set": {"test_int": 100}},
        filter_query={"test_str": "kipasa"},
    )
    result = []
    async for document in collection.find({"test_str": "kipasa"}):
        result.append(document)
        assert document.test_int == 100
    assert len(result) == 2


async def test_update_one_wrong_type(collection):
    with pytest.raises(TypeError):
        await collection.update_one("wrong_type", update_query={})


async def test_delete_one(collection, document_not_inserted, loop):
    document = document_not_inserted
    inserted_document = await collection.insert_one(document)
    await collection.delete_one(inserted_document)
    new_document = await collection.get_one(inserted_document.id)
    assert new_document is None


async def test_delete_many(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await collection.delete_many({"test_str": "uno"})
    documents = await collection.all().to_list()
    assert len(documents) == 3


async def test_delete_many_not_found(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await collection.delete_many({"test_str": "wrong"})
    documents = await collection.all().to_list()
    assert len(documents) == 7


async def test_delete_all(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    await collection.delete_all()
    documents = await collection.all().to_list()
    assert len(documents) == 0


async def test_delete_one_wrong_type(collection):
    with pytest.raises(TypeError):
        await collection.delete_one("wrong_type")


async def test_find_one(collection, document_not_inserted):
    for s in ["one", "two", "three"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    new_document = await collection.find_one({"test_str": "one"})
    assert new_document.test_str == "one"


async def test_find_one_not_found(collection, document_not_inserted):
    for s in ["one", "two", "three"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    new_document = await collection.find_one({"test_str": "wrong"})
    assert new_document is None


async def test_find_one_more_than_one(collection, document_not_inserted):
    for s in ["one", "one", "three"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    new_document = await collection.find_one({"test_str": "one"})
    assert new_document.test_str == "one"


async def test_get_one(collection, document_not_inserted):
    documents = []
    for s in ["one", "two", "three"]:
        document_not_inserted.test_str = s
        doc = await collection.insert_one(document_not_inserted)
        documents.append(doc.id)
    new_document = await collection.get_one(documents[0])
    assert new_document.test_str == "one"


async def test_get_one_not_found(collection, document_not_inserted):
    documents = []
    for s in ["one", "two", "three"]:
        document_not_inserted.test_str = s
        doc = await collection.insert_one(document_not_inserted)
        documents.append(doc.id)
    new_document = await collection.get_one(PydanticObjectId())
    assert new_document is None


async def test_get_one_wrong_type(collection):
    with pytest.raises(TypeError):
        await collection.get_one("id")


async def test_find(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    num = 0
    async for _ in collection.find({"test_str": "uno"}):
        num += 1
    assert num == 4


async def test_find_to_list(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = await collection.find({"test_str": "uno"}).to_list()
    assert len(result) == 4


async def test_find_to_list_2_items(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = await collection.find({"test_str": "uno"}).to_list(length=2)
    assert len(result) == 2


async def test_find_not_found(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    async for _ in collection.find({"test_str": "wrong"}):
        assert False


async def test_all(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    num = 0
    async for _ in collection.all():
        num += 1
    assert num == 7


async def test_aggregate(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = []
    async for i in collection.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ):
        result.append(i)
    assert len(result) == 3
    assert {"_id": "cuatro", "total": 42} in result
    assert {"_id": "dos", "total": 84} in result
    assert {"_id": "uno", "total": 168} in result


async def test_aggregate_to_list(collection, document_not_inserted):
    for s in ["uno", "uno", "uno", "uno", "dos", "dos", "cuatro"]:
        document_not_inserted.test_str = s
        await collection.insert_one(document_not_inserted)
    result = await collection.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ).to_list()
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
    async for i in collection.aggregate(
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
