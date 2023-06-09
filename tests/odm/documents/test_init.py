import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from beanie import Document, init_beanie, Indexed
from beanie.exceptions import CollectionWasNotInitialized
from beanie.odm.utils.projection import get_projection
from tests.odm.models import (
    DocumentTestModel,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithIndexFlagsAliases,
    DocumentTestModelWithSimpleIndex,
    DocumentTestModelWithIndexFlags,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelStringImport,
    DocumentTestModelWithDroppedIndex,
    DocumentWithIndexMerging2,
    DocumentWithCustomInit,
)
from pymongo import IndexModel


async def test_init_collection_was_not_initialized():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(CollectionWasNotInitialized):
        NewDocument(test_str="test")


async def test_init_connection_string(settings):
    class NewDocumentCS(Document):
        test_str: str

    await init_beanie(
        connection_string=settings.mongodb_dsn, document_models=[NewDocumentCS]
    )
    assert (
        NewDocumentCS.get_motor_collection().database.name
        == settings.mongodb_dsn.split("/")[-1]
    )


async def test_init_wrong_params(settings, db):
    class NewDocumentCS(Document):
        test_str: str

    with pytest.raises(ValueError):
        await init_beanie(
            database=db,
            connection_string=settings.mongodb_dsn,
            document_models=[NewDocumentCS],
        )

    with pytest.raises(ValueError):
        await init_beanie(document_models=[NewDocumentCS])

    with pytest.raises(ValueError):
        await init_beanie(connection_string=settings.mongodb_dsn)


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


async def test_flagged_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithIndexFlags.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info["test_int_1"] == {
        "key": [("test_int", 1)],
        "sparse": True,
        "v": 2,
    }
    assert index_info["test_str_-1"] == {
        "key": [("test_str", -1)],
        "unique": True,
        "v": 2,
    }


async def test_flagged_index_creation_with_alias():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithIndexFlagsAliases.get_motor_collection()
    )
    index_info = await collection.index_information()
    assert index_info["testInt_1"] == {
        "key": [("testInt", 1)],
        "sparse": True,
        "v": 2,
    }
    assert index_info["testStr_-1"] == {
        "key": [("testStr", -1)],
        "unique": True,
        "v": 2,
    }


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
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
    )

    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
        allow_index_dropping=True,
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


async def test_index_dropping_is_not_allowed_as_default(db):
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
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
        "test_doc": 1,
        "revision_id": 1,
    }


async def test_index_recreation(db):
    class Sample1(Document):
        name: Indexed(str, unique=True)

        class Settings:
            name = "sample"

    class Sample2(Document):
        name: str
        status: str = "active"

        class Settings:
            indexes = [
                IndexModel(
                    "name",
                    unique=True,
                    partialFilterExpression={"is_active": {"$eq": "active"}},
                ),
            ]
            name = "sample"

    await db.drop_collection("sample")

    await init_beanie(
        database=db,
        document_models=[Sample1],
    )

    await init_beanie(
        database=db, document_models=[Sample2], allow_index_dropping=True
    )

    await db.drop_collection("sample")


async def test_merge_indexes():
    assert await DocumentWithIndexMerging2.get_motor_collection().index_information() == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "s0_1": {"key": [("s0", 1)], "v": 2},
        "s1_1": {"key": [("s1", 1)], "v": 2},
        "s2_-1": {"key": [("s2", -1)], "v": 2},
        "s3_index": {"key": [("s3", -1)], "v": 2},
        "s4_index": {"key": [("s4", 1)], "v": 2},
    }


async def test_custom_init():
    assert DocumentWithCustomInit.s == "TEST2"
