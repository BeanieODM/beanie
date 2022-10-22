import pytest
from motor.motor_asyncio import AsyncIOMotorCollection
from yarl import URL

from beanie.sync.odm import Document, init_beanie
from beanie.exceptions import CollectionWasNotInitialized
from beanie.sync.odm.utils.projection import get_projection
from tests.sync.models import (
    DocumentTestModel,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithIndexFlagsAliases,
    DocumentTestModelWithSimpleIndex,
    DocumentTestModelWithIndexFlags,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelStringImport,
    DocumentTestModelWithDroppedIndex,
)


def test_init_collection_was_not_initialized():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(CollectionWasNotInitialized):
        NewDocument(test_str="test")


def test_init_connection_string(settings):
    class NewDocumentCS(Document):
        test_str: str

    init_beanie(
        connection_string=settings.mongodb_dsn, document_models=[NewDocumentCS]
    )
    assert (
        NewDocumentCS.get_motor_collection().database.name
        == URL(settings.mongodb_dsn).path[1:]
    )


def test_init_wrong_params(settings, db):
    class NewDocumentCS(Document):
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
        DocumentTestModelWithCustomCollectionName.get_motor_collection()
    )
    assert collection.name == "custom"


def test_simple_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithSimpleIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info["test_int_1"] == {"key": [("test_int", 1)], "v": 2}
    assert index_info["test_str_text"]["key"] == [
        ("_fts", "text"),
        ("_ftsx", 1),
    ]


def test_flagged_index_creation():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithIndexFlags.get_motor_collection()
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
        DocumentTestModelWithIndexFlagsAliases.get_motor_collection()
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
        DocumentTestModelWithComplexIndex.get_motor_collection()
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
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
        allow_index_dropping=True,
    )

    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
    )
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
    }


def test_index_dropping_is_not_allowed(db):
    init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
        allow_index_dropping=False,
    )

    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
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
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
    )

    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithComplexIndex.get_motor_collection()
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
            "tests.sync.models.DocumentTestModelStringImport",
        ],
    )
    document = DocumentTestModelStringImport(test_int=1)
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
    projection = get_projection(DocumentTestModel)
    assert projection == {
        "_id": 1,
        "test_int": 1,
        "test_list": 1,
        "test_str": 1,
        "test_doc": 1,
        "revision_id": 1,
    }
