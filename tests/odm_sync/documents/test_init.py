import pytest
from motor.motor_asyncio import AsyncIOMotorCollection
from yarl import URL

from beanie.odm_sync import SyncDocument, init_beanie
from beanie.exceptions import CollectionWasNotInitialized
from beanie.odm_sync.utils.projection import get_projection
from tests.odm_sync.models import (
    SyncDocumentTestModel,
    SyncDocumentTestModelWithCustomCollectionName,
    SyncDocumentTestModelWithIndexFlagsAliases,
    SyncDocumentTestModelWithSimpleIndex,
    SyncDocumentTestModelWithIndexFlags,
    SyncDocumentTestModelWithComplexIndex,
    SyncDocumentTestModelStringImport,
    SyncDocumentTestModelWithDroppedIndex,
)


def test_init_collection_was_not_initialized():
    class NewDocument(SyncDocument):
        test_str: str

    with pytest.raises(CollectionWasNotInitialized):
        NewDocument(test_str="test")


def test_init_connection_string(settings):
    class NewDocumentCS(SyncDocument):
        test_str: str

    init_beanie(
        connection_string=settings.mongodb_dsn, document_models=[NewDocumentCS]
    )
    assert (
        NewDocumentCS.get_motor_collection().database.name
        == URL(settings.mongodb_dsn).path[1:]
    )


def test_init_wrong_params(settings, db):
    class NewDocumentCS(SyncDocument):
        test_str: str

    with pytest.raises(ValueError):
        init_beanie(
            database=db,
            connection_string=settings.mongodb_dsn,
            document_models=[NewDocumentCS],
        )

    with pytest.raises(ValueError):
        init_beanie(document_models=[NewDocumentCS])

    with pytest.raises(ValueError):
        init_beanie(connection_string=settings.mongodb_dsn)


def test_collection_with_custom_name():
    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithCustomCollectionName.get_motor_collection()
    )
    assert collection.name == "custom"


def test_simple_index_creation():
    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithSimpleIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info["test_int_1"] == {"key": [("test_int", 1)], "v": 2}
    assert index_info["test_str_text"]["key"] == [
        ("_fts", "text"),
        ("_ftsx", 1),
    ]


def test_flagged_index_creation():
    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithIndexFlags.get_motor_collection()
    )
    index_info = collection.index_information()
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


def test_flagged_index_creation_with_alias():
    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithIndexFlagsAliases.get_motor_collection()
    )
    index_info = collection.index_information()
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


def test_complex_index_creation():
    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {"key": [("test_str", -1)], "v": 2},
    }


def test_index_dropping_is_allowed(db):
    init_beanie(
        database=db, document_models=[SyncDocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[SyncDocumentTestModelWithDroppedIndex],
        allow_index_dropping=True,
    )

    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
    }


def test_index_dropping_is_not_allowed(db):
    init_beanie(
        database=db, document_models=[SyncDocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[SyncDocumentTestModelWithDroppedIndex],
        allow_index_dropping=False,
    )

    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {"key": [("test_str", -1)], "v": 2},
    }


def test_index_dropping_is_not_allowed_as_default(db):
    init_beanie(
        database=db, document_models=[SyncDocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[SyncDocumentTestModelWithDroppedIndex],
    )

    collection: AsyncIOMotorCollection = (
        SyncDocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {"key": [("test_str", -1)], "v": 2},
    }


def test_document_string_import(db):
    init_beanie(
        database=db,
        document_models=[
            "tests.odm_sync.models.SyncDocumentTestModelStringImport",
        ],
    )
    document = SyncDocumentTestModelStringImport(test_int=1)
    assert document.id is None
    document.insert()
    assert document.id is not None

    with pytest.raises(ValueError):
        init_beanie(
            database=db,
            document_models=[
                "tests",
            ],
        )

    with pytest.raises(AttributeError):
        init_beanie(
            database=db,
            document_models=[
                "tests.wrong",
            ],
        )


def test_projection():
    projection = get_projection(SyncDocumentTestModel)
    assert projection == {
        "_id": 1,
        "test_int": 1,
        "test_list": 1,
        "test_str": 1,
        "test_doc": 1,
        "revision_id": 1,
    }
