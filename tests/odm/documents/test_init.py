import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from beanie import Document, init_beanie
from beanie.exceptions import CollectionWasNotInitialized
from beanie.odm.utils.projection import get_projection
from tests.odm.models import (
    DocumentTestModel,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithSimpleIndex,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelStringImport,
    DocumentTestModelWithDroppedIndex,
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


async def test_simple_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithSimpleIndex.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info["test_int_1"] == {"key": [("test_int", 1)], "v": 2}
    assert index_info["test_str_text"]["key"] == [
        ("_fts", "text"),
        ("_ftsx", 1),
    ]


async def test_complex_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {"key": [("test_str", -1)], "v": 2},
    }


async def test_index_dropping_is_allowed(db):
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithDroppedIndex]
    )

    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
    }


async def test_index_dropping_is_not_allowed(db):
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
        allow_index_dropping=False,
    )

    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
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
            "tests.odm.models.DocumentTestModelStringImport",
        ],
    )
    document = DocumentTestModelStringImport(test_int=1)
    assert document.id is None
    await document.insert()
    assert document.id is not None

    with pytest.raises(ValueError):
        await init_beanie(
            database=db,
            document_models=[
                "tests",
            ],
        )

    with pytest.raises(AttributeError):
        await init_beanie(
            database=db,
            document_models=[
                "tests.wrong",
            ],
        )


async def test_projection():
    projection = get_projection(DocumentTestModel)
    assert projection == {
        "_id": 1,
        "test_int": 1,
        "test_list": 1,
        "test_str": 1,
    }
