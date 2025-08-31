import json

import pytest
from pymongo import IndexModel
from pymongo.errors import OperationFailure

from beanie import Document, Indexed, init_beanie
from beanie.odm.fields import IndexModelField
from tests.odm.models import (
    Color,
    DocumentTestModelIndexFlagsAnnotated,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelWithIndexFlags,
    DocumentTestModelWithIndexFlagsAliases,
    DocumentTestModelWithSimpleIndex,
    DocumentWithCompoundIndexes,
    DocumentWithCompoundIndexesDirectionConflict,
    DocumentWithCompoundIndexesFieldOrderConflict,
    DocumentWithIndexMerging2,
    DocumentWithMultipleIndexesOnSameField,
    DocumentWithMultipleIndexesOnSameFieldWithSameOptions,
    DocumentWithMultipleSameIndexesOptionOrderConflict,
    DocumentWithMultipleSameIndexesWithDifferentName,
)
from tests.utils import is_mongo_version_5_or_higher


async def test_indexmodelfield_equality():
    idx1 = IndexModel("a", name="idx1")
    idx2 = IndexModel("a", name="idx2")
    field1 = IndexModelField(idx1)
    field2 = IndexModelField(idx2)

    # Not equal because index name is different
    assert field1 != field2

    idx1 = IndexModel([("a", 1)])
    idx2 = IndexModel([("a", -1)])
    field1 = IndexModelField(idx1)
    field2 = IndexModelField(idx2)

    # Not equal because direction is different
    assert field1 != field2

    idx1 = IndexModel([("a", 1), ("b", 1)])
    idx2 = IndexModel([("b", 1), ("a", 1)])

    field1 = IndexModelField(idx1)
    field2 = IndexModelField(idx2)

    # Not equal because order of fields in a compound index matters
    assert field1 != field2


async def test_simple_index_creation():
    collection = DocumentTestModelWithSimpleIndex.get_pymongo_collection()
    index_info = await collection.index_information()
    assert index_info["test_int_1"] == {"key": [("test_int", 1)], "v": 2}
    assert index_info["test_str_text"]["key"] == [
        ("_fts", "text"),
        ("_ftsx", 1),
    ]


async def test_flagged_index_creation():
    collection = DocumentTestModelWithIndexFlags.get_pymongo_collection()
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
    collection = (
        DocumentTestModelWithIndexFlagsAliases.get_pymongo_collection()
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


async def test_annotated_index_creation():
    collection = DocumentTestModelIndexFlagsAnnotated.get_pymongo_collection()
    index_info = await collection.index_information()
    assert index_info["str_index_text"]["key"] == [
        ("_fts", "text"),
        ("_ftsx", 1),
    ]
    assert index_info["str_index_annotated_1"] == {
        "key": [("str_index_annotated", 1)],
        "v": 2,
    }

    assert index_info["uuid_index_annotated_1"] == {
        "key": [("uuid_index_annotated", 1)],
        "unique": True,
        "v": 2,
    }
    if "uuid_index" in index_info:
        assert index_info["uuid_index"] == {
            "key": [("uuid_index", 1)],
            "unique": True,
            "v": 2,
        }


async def test_complex_index_creation():
    collection = DocumentTestModelWithComplexIndex.get_pymongo_collection()
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


async def test_index_on_custom_types(db):
    class Sample1(Document):
        name: Indexed(Color, unique=True)

        class Settings:
            name = "sample"

    await db.drop_collection("sample")

    await init_beanie(
        database=db,
        document_models=[Sample1],
    )

    await db.drop_collection("sample")


async def test_merge_indexes():
    collection = DocumentWithIndexMerging2.get_pymongo_collection()
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "s0_1": {"key": [("s0", 1)], "v": 2},
        "s1_1": {"key": [("s1", 1)], "v": 2},
        "s2_-1": {"key": [("s2", -1)], "v": 2},
        "s3_index": {"key": [("s3", -1)], "v": 2},
        "s4_index": {"key": [("s4", 1)], "v": 2},
    }


async def test_merge_multiple_indexes_on_same_field_with_same_name_and_options(
    db,
):
    await init_beanie(
        database=db,
        document_models=[
            DocumentWithMultipleIndexesOnSameFieldWithSameOptions
        ],
    )

    collection = DocumentWithMultipleIndexesOnSameFieldWithSameOptions.get_pymongo_collection()
    index_info = await collection.index_information()

    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "status_1": {"v": 2, "key": [["status", 1]]},
    }

    await collection.drop()


async def test_merge_multiple_indexes_on_same_field_with_different_name_but_same_options(
    db,
):
    await init_beanie(
        database=db,
        document_models=[DocumentWithMultipleSameIndexesWithDifferentName],
    )
    collection = DocumentWithMultipleSameIndexesWithDifferentName.get_pymongo_collection()
    index_info = await collection.index_information()

    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "processing_expire_31": {
            "v": 2,
            "key": [["created_at", 1]],
            "partialFilterExpression": {"status": "processing"},
            "expireAfterSeconds": 30,
        },
    }

    await collection.drop()


async def test_merge_multiple_indexes_on_same_field_with_different_name_and_options(
    db,
):
    if not is_mongo_version_5_or_higher():
        # Not supported on MongoDB 4.4, fails due to a duplicate index
        with pytest.raises(OperationFailure):
            await init_beanie(
                database=db,
                document_models=[DocumentWithMultipleIndexesOnSameField],
            )
        return

    await init_beanie(
        database=db,
        document_models=[DocumentWithMultipleIndexesOnSameField],
    )

    collection = (
        DocumentWithMultipleIndexesOnSameField.get_pymongo_collection()
    )
    index_info = await collection.index_information()

    # Expect both indexes since they have different name and options
    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "status_-1": {"v": 2, "key": [["status", -1]]},
        "processing_expire_30": {
            "v": 2,
            "key": [["created_at", 1]],
            "partialFilterExpression": {"status": "processing"},
            "expireAfterSeconds": 30,
        },
        "unpaid_expire_900": {
            "v": 2,
            "key": [["created_at", 1]],
            "partialFilterExpression": {"status": "unpaid"},
            "expireAfterSeconds": 900,
        },
    }

    await collection.drop()


async def test_merge_compound_indexes(db):
    if not is_mongo_version_5_or_higher():
        # Not supported on MongoDB 4.4, fails due to a duplicate index
        with pytest.raises(OperationFailure):
            await init_beanie(
                database=db,
                document_models=[DocumentWithCompoundIndexes],
            )
        return

    await init_beanie(
        database=db, document_models=[DocumentWithCompoundIndexes]
    )
    collection = DocumentWithCompoundIndexes.get_pymongo_collection()
    index_info = await collection.index_information()

    # Expect all indexes since they have different keys or options
    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "field_a_1_field_b_1": {
            "v": 2,
            "key": [["field_a", 1], ["field_b", 1]],
        },
        "field_a_-1_field_b_-1": {
            "v": 2,
            "key": [["field_a", -1], ["field_b", -1]],
        },
        "compound_unique": {
            "v": 2,
            "key": [["field_a", 1], ["field_b", 1]],
            "unique": True,
        },
        "ttl_index": {
            "v": 2,
            "key": [["created_at", 1]],
            "expireAfterSeconds": 60,
        },
    }

    await collection.drop()


async def test_merge_compound_indexes_direction_conflict(db):
    await init_beanie(
        database=db,
        document_models=[DocumentWithCompoundIndexesDirectionConflict],
    )
    collection = (
        DocumentWithCompoundIndexesDirectionConflict.get_pymongo_collection()
    )
    index_info = await collection.index_information()

    # Expect both, because directions differ
    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "a_1_b_-1": {"v": 2, "key": [["a", 1], ["b", -1]]},
        "a_-1_b_-1": {"v": 2, "key": [["a", -1], ["b", -1]]},
    }

    await collection.drop()


async def test_merge_compound_indexes_field_order_conflict(db):
    await init_beanie(
        database=db,
        document_models=[DocumentWithCompoundIndexesFieldOrderConflict],
    )
    collection = (
        DocumentWithCompoundIndexesFieldOrderConflict.get_pymongo_collection()
    )
    index_info = await collection.index_information()

    # Expect both, because compound order matters
    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "a_1_b_1": {"v": 2, "key": [["a", 1], ["b", 1]]},
        "b_1_a_1": {"v": 2, "key": [["b", 1], ["a", 1]]},
    }

    await collection.drop()


async def test_merge_indexes_options_order_conflict(db):
    await init_beanie(
        database=db,
        document_models=[DocumentWithMultipleSameIndexesOptionOrderConflict],
    )
    collection = DocumentWithMultipleSameIndexesOptionOrderConflict.get_pymongo_collection()
    index_info = await collection.index_information()

    # Expect only one index, since options order shouldn't matter
    assert json.loads(json.dumps(index_info)) == {
        "_id_": {"v": 2, "key": [["_id", 1]]},
        "a_1": {"v": 2, "key": [["a", 1]], "unique": True, "sparse": True},
    }

    await collection.drop()
