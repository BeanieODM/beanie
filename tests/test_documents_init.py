import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from beanie import Document, init_beanie
from beanie.exceptions import CollectionWasNotInitialized
from tests.models import (
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithIndex,
    DocumentTestModelStringImport,
)


async def test_init():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(CollectionWasNotInitialized):
        NewDocument(test_str="test")


async def test_collection_with_custom_name():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithCustomCollectionName.get_motor_collection()
    )
    assert collection.name == "custom"


async def test_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithIndex.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_indexed_int_1": {"key": [("test_indexed_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {"key": [("test_str", -1)], "v": 2},
    }


async def test_document_string_import(db):
    await init_beanie(
        database=db,
        document_models=[
            "tests.models.DocumentTestModelStringImport",
        ],
    )
    document = DocumentTestModelStringImport(test_int=1)
    assert document.id is None
    await document.create()
    assert document.id is not None
