from importlib.metadata import version

import pytest
from pymongo import AsyncMongoClient

from beanie import Document, init_beanie
from beanie import __version__ as beanie_version
from beanie.exceptions import CollectionWasNotInitialized
from tests.odm.models import (
    Color,
    DocumentTestModelStringImport,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithDroppedIndex,
    DocumentToBeLinked,
    DocumentWithCustomInit,
    DocumentWithLink,
    DocumentWithListLink,
    DocumentWithOptionalTypingOptionalBackLink,
    DocumentWithOptionalTypingOptionalLink,
    DocumentWithUnionTypeExpressionOptionalBackLink,
    DocumentWithUnionTypeExpressionOptionalLink,
)


def test_custom_init():
    assert DocumentWithCustomInit.s == "TEST2"


async def test_init_connection_string(settings):
    class NewDocumentCS(Document):
        test_str: str

    try:
        await init_beanie(
            connection_string=settings.mongodb_dsn,
            document_models=[NewDocumentCS],
        )
        assert (
            NewDocumentCS.get_pymongo_collection().database.name
            == settings.mongodb_dsn.split("/")[-1]
        )

    finally:
        await NewDocumentCS.get_pymongo_collection().database.client.close()


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


async def test_metadata_connection_string(settings):
    class NewDocument(Document):
        test_str: str

    try:
        await init_beanie(
            connection_string=settings.mongodb_dsn,
            document_models=[NewDocument],
        )

        metadata = NewDocument.get_pymongo_collection().database.client.options.pool_options.metadata
        assert "beanie" in metadata["driver"]["name"]
        assert beanie_version in metadata["driver"]["version"]

    finally:
        await NewDocument.get_pymongo_collection().database.client.close()


@pytest.mark.skipif(
    version("pymongo") < "4.14",
    reason="append_metadata was added in PyMongo 4.14",
)
async def test_metadata_database(settings):
    class NewDocument(Document):
        test_str: str

    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(database=db, document_models=[NewDocument])

        metadata = NewDocument.get_pymongo_collection().database.client.options.pool_options.metadata
        assert "beanie" in metadata["driver"]["name"]
        assert beanie_version in metadata["driver"]["version"]


async def test_init_document_models_string_import(settings):
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        try:
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
        finally:
            await DocumentTestModelStringImport.get_pymongo_collection().drop()


def test_init_collection_was_not_initialized():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(CollectionWasNotInitialized):
        NewDocument(test_str="test")


def test_collection_with_custom_name():
    collection = (
        DocumentTestModelWithCustomCollectionName.get_pymongo_collection()
    )
    assert collection.name == "custom"


async def test_init_document_can_inherit_and_extend_settings(settings):
    class Sample1(Document):
        class Settings:
            name = "sample1"
            bson_encoders = {Color: lambda x: x.value}

    class Sample2(Sample1):
        class Settings(Sample1.Settings):
            name = "sample2"

    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[Sample2],
        )

        assert Sample2.get_settings().bson_encoders != {}
        assert Sample2.get_settings().name == "sample2"


async def test_init_document_with_union_type_expression_optional_link(db):
    await init_beanie(
        database=db,
        document_models=[
            DocumentToBeLinked,
            DocumentWithUnionTypeExpressionOptionalLink,
        ],
    )

    assert (
        DocumentWithUnionTypeExpressionOptionalLink.get_link_fields().keys()
        == {"link", "link_list"}
    )


async def test_init_document_with_typing_optional_link(db):
    await init_beanie(
        database=db,
        document_models=[
            DocumentToBeLinked,
            DocumentWithOptionalTypingOptionalLink,
        ],
    )

    assert DocumentWithOptionalTypingOptionalLink.get_link_fields().keys() == {
        "link",
        "link_list",
    }


async def test_init_document_with_union_type_expression_optional_back_link(db):
    await init_beanie(
        database=db,
        document_models=[
            DocumentWithUnionTypeExpressionOptionalBackLink,
            DocumentWithListLink,
            DocumentWithLink,
        ],
    )

    assert (
        DocumentWithUnionTypeExpressionOptionalBackLink.get_link_fields().keys()
        == {
            "back_link_list",
            "back_link",
        }
    )


async def test_init_document_with_typing_optional_back_link(db):
    await init_beanie(
        database=db,
        document_models=[
            DocumentWithOptionalTypingOptionalBackLink,
            DocumentWithListLink,
            DocumentWithLink,
        ],
    )

    assert (
        DocumentWithOptionalTypingOptionalBackLink.get_link_fields().keys()
        == {"back_link_list", "back_link"}
    )


async def test_init_allow_index_dropping_is_enabled(db):
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    collection = DocumentTestModelWithComplexIndex.get_pymongo_collection()

    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
        allow_index_dropping=True,
    )

    collection = DocumentTestModelWithComplexIndex.get_pymongo_collection()
    index_info = await collection.index_information()

    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
    }


async def test_init_allow_index_dropping_is_disabled_by_default(db):
    await init_beanie(
        database=db, document_models=[DocumentTestModelWithComplexIndex]
    )
    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDroppedIndex],
    )

    collection = DocumentTestModelWithComplexIndex.get_pymongo_collection()
    index_info = await collection.index_information()

    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "test_int_1": {"key": [("test_int", 1)], "v": 2},
        "test_int_1_test_str_-1": {
            "key": [("test_int", 1), ("test_str", -1)],
            "v": 2,
        },
        "test_string_index_DESCENDING": {
            "key": [("test_str", -1)],
            "v": 2,
        },
    }


async def test_init_beanie_with_skip_indexes(settings):
    class NewDocument(Document):
        test_str: str

        class Settings:
            indexes = ["test_str"]

    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[NewDocument],
            skip_indexes=True,
        )

        # To force collection creation
        await NewDocument(test_str="Roman Right").save()

        collection = NewDocument.get_pymongo_collection()
        index_info = await collection.index_information()

        # Only the default _id index should be present
        assert len(index_info) == 1
