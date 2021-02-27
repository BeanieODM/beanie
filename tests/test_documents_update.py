import pytest

from beanie.exceptions import DocumentWasNotSaved, DocumentNotFound
from beanie.fields import PydanticObjectId
from tests.models import DocumentTestModel, SubDocument


# REPLACE


async def test_replace_one(document):
    new_doc = DocumentTestModel(
        test_int=0, test_str="REPLACED_VALUE", test_list=[]
    )
    await DocumentTestModel.replace_one({"_id": document.id}, new_doc)
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_str == "REPLACED_VALUE"


async def test_replace(document):
    document.test_str = "REPLACED_VALUE"
    await document.replace()
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_str == "REPLACED_VALUE"


async def test_replace_not_saved(document_not_inserted):
    with pytest.raises(DocumentWasNotSaved):
        await document_not_inserted.replace()


async def test_replace_not_found(document_not_inserted):
    document_not_inserted.id = PydanticObjectId()
    with pytest.raises(DocumentNotFound):
        await document_not_inserted.replace()


# UPDATE


async def test_update_one(document):
    await DocumentTestModel.update_one(
        update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
        filter_query={"_id": document.id, "test_list.test_str": "foo"},
    )
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_list[0].test_str == "foo_foo"


async def test_update_many(documents):
    await documents(10, "foo")
    await documents(7, "bar")
    await DocumentTestModel.update_many(
        update_query={"$set": {"test_str": "bar"}},
        filter_query={"test_str": "foo"},
    )
    bar_documetns = await DocumentTestModel.find_many(
        {"test_str": "bar"}
    ).to_list()
    assert len(bar_documetns) == 17
    foo_documetns = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    assert len(foo_documetns) == 0


async def test_update_all(documents):
    await documents(10, "foo")
    await documents(7, "bar")
    await DocumentTestModel.update_all(
        update_query={"$set": {"test_str": "smth_else"}},
    )
    bar_documetns = await DocumentTestModel.find_many(
        {"test_str": "bar"}
    ).to_list()
    assert len(bar_documetns) == 0
    foo_documetns = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    assert len(foo_documetns) == 0
    smth_else_documetns = await DocumentTestModel.find_many(
        {"test_str": "smth_else"}
    ).to_list()
    assert len(smth_else_documetns) == 17


async def test_update(document):
    buf_len = len(document.test_list)
    to_insert = SubDocument(test_str="test")
    await document.update(
        update_query={"$push": {"test_list": to_insert.dict()}}
    )
    new_document = await DocumentTestModel.get(document.id)
    assert len(new_document.test_list) == buf_len + 1
