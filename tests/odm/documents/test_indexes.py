"""Comprehensive regression tests for index creation and merging logic.

Covers: IndexModelField equality, merge_indexes deduplication, same-field
multiple indexes, Annotated/Indexed, aliases, compound/direction conflicts,
option-order canonicalization, field-level vs Settings interaction, and
backward compatibility with inheritance-based merge.
"""

import json

from pymongo import ASCENDING, DESCENDING, AsyncMongoClient, IndexModel

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

# ---------------------------------------------------------------------------
# Unit tests: IndexModelField equality
# ---------------------------------------------------------------------------


class TestIndexModelFieldEquality:
    """IndexModelField.__eq__ uses (fields, options) including name."""

    def test_different_names_not_equal(self):
        field1 = IndexModelField(IndexModel("a", name="idx1"))
        field2 = IndexModelField(IndexModel("a", name="idx2"))
        assert field1 != field2

    def test_different_directions_not_equal(self):
        field1 = IndexModelField(IndexModel([("a", 1)]))
        field2 = IndexModelField(IndexModel([("a", -1)]))
        assert field1 != field2

    def test_compound_field_order_not_equal(self):
        field1 = IndexModelField(IndexModel([("a", 1), ("b", 1)]))
        field2 = IndexModelField(IndexModel([("b", 1), ("a", 1)]))
        assert field1 != field2


# ---------------------------------------------------------------------------
# Unit tests: merge_indexes pure logic
# ---------------------------------------------------------------------------


class TestMergeIndexesPreservesDifferentOptions:
    """Two indexes on same field with different options must both survive."""

    def test_different_partial_filters_and_ttl(self):
        """User's original bug: two TTL indexes on same field with different
        partialFilterExpression should both be preserved."""
        index1 = IndexModelField(
            IndexModel(
                [("created_at", 1)],
                name="processing_expire_30",
                expireAfterSeconds=30,
                partialFilterExpression={"status": "processing"},
            )
        )
        index2 = IndexModelField(
            IndexModel(
                [("created_at", 1)],
                name="unpaid_expire_900",
                expireAfterSeconds=900,
                partialFilterExpression={"status": "unpaid"},
            )
        )

        merged = IndexModelField.merge_indexes([index1], [index2])

        assert len(merged) == 2
        assert {idx.name for idx in merged} == {
            "processing_expire_30",
            "unpaid_expire_900",
        }

    def test_different_sparse_vs_unique(self):
        """Same field, one sparse and one unique — both kept."""
        index1 = IndexModelField(
            IndexModel([("email", 1)], name="email_sparse", sparse=True)
        )
        index2 = IndexModelField(
            IndexModel([("email", 1)], name="email_unique", unique=True)
        )

        merged = IndexModelField.merge_indexes([index1], [index2])

        assert len(merged) == 2
        assert {idx.name for idx in merged} == {"email_sparse", "email_unique"}


class TestMergeIndexesDeduplication:
    """Indexes with same fields and same options should deduplicate."""

    def test_same_options_different_names_deduplicates(self):
        """Same field + same options but different names: the last one wins."""
        index1 = IndexModelField(
            IndexModel(
                [("created_at", 1)], name="idx_a", expireAfterSeconds=30
            )
        )
        index2 = IndexModelField(
            IndexModel(
                [("created_at", 1)], name="idx_b", expireAfterSeconds=30
            )
        )

        merged = IndexModelField.merge_indexes([index1], [index2])

        assert len(merged) == 1
        assert merged[0].name == "idx_b"

    def test_identical_indexes_deduplicate(self):
        index = IndexModelField(IndexModel([("field", 1)], name="field_1"))
        merged = IndexModelField.merge_indexes([index], [index])
        assert len(merged) == 1

    def test_right_list_overwrites_left(self):
        """new_indexes (right) wins over existing_indexes (left)."""
        index_old = IndexModelField(
            IndexModel([("x", 1)], name="x_1", unique=True)
        )
        index_new = IndexModelField(
            IndexModel([("x", -1)], name="x_-1", unique=True)
        )

        merged = IndexModelField.merge_indexes([index_old], [index_new])

        assert len(merged) == 1
        assert merged[0].name == "x_-1"


class TestMergeIndexesSingleFieldDirection:
    """Single-field indexes ignore direction for dedup purposes."""

    def test_ascending_vs_descending_last_wins(self):
        index_asc = IndexModelField(IndexModel([("ts", ASCENDING)]))
        index_desc = IndexModelField(IndexModel([("ts", DESCENDING)]))

        merged = IndexModelField.merge_indexes([index_asc], [index_desc])

        assert len(merged) == 1
        assert dict(merged[0].index.document["key"])["ts"] == DESCENDING

    def test_direction_ignored_but_options_differentiate(self):
        """Same field, different direction AND different options → both kept."""
        index1 = IndexModelField(
            IndexModel([("ts", ASCENDING)], expireAfterSeconds=60)
        )
        index2 = IndexModelField(IndexModel([("ts", DESCENDING)], unique=True))

        merged = IndexModelField.merge_indexes([index1], [index2])

        assert len(merged) == 2


class TestMergeIndexesCompound:
    """Compound indexes preserve full (field, direction) ordering in key."""

    def test_same_fields_different_direction_both_kept(self):
        index1 = IndexModelField(
            IndexModel([("a", ASCENDING), ("b", ASCENDING)])
        )
        index2 = IndexModelField(
            IndexModel([("a", ASCENDING), ("b", DESCENDING)])
        )

        merged = IndexModelField.merge_indexes([index1], [index2])
        assert len(merged) == 2

    def test_same_fields_different_order_both_kept(self):
        index1 = IndexModelField(
            IndexModel([("a", ASCENDING), ("b", ASCENDING)])
        )
        index2 = IndexModelField(
            IndexModel([("b", ASCENDING), ("a", ASCENDING)])
        )

        merged = IndexModelField.merge_indexes([index1], [index2])
        assert len(merged) == 2

    def test_identical_compound_deduplicates(self):
        index1 = IndexModelField(
            IndexModel([("a", 1), ("b", -1)], name="ab_idx")
        )
        index2 = IndexModelField(
            IndexModel([("a", 1), ("b", -1)], name="ab_idx_v2")
        )

        merged = IndexModelField.merge_indexes([index1], [index2])
        assert len(merged) == 1
        assert merged[0].name == "ab_idx_v2"


class TestMergeIndexesOptionsCanonicalization:
    """Options with different key ordering should be treated as equal."""

    def test_partial_filter_key_order_irrelevant(self):
        index1 = IndexModelField(
            IndexModel(
                [("x", 1)],
                name="idx1",
                partialFilterExpression={"status": "a", "type": "b"},
            )
        )
        index2 = IndexModelField(
            IndexModel(
                [("x", 1)],
                name="idx2",
                partialFilterExpression={"type": "b", "status": "a"},
            )
        )

        merged = IndexModelField.merge_indexes([index1], [index2])
        assert len(merged) == 1
        assert merged[0].name == "idx2"

    def test_nested_dict_options_canonicalized(self):
        index1 = IndexModelField(
            IndexModel(
                [("x", 1)],
                name="idx1",
                partialFilterExpression={"$and": [{"a": 1}, {"b": 2}]},
            )
        )
        index2 = IndexModelField(
            IndexModel(
                [("x", 1)],
                name="idx2",
                partialFilterExpression={"$and": [{"a": 1}, {"b": 2}]},
            )
        )

        merged = IndexModelField.merge_indexes([index1], [index2])
        assert len(merged) == 1


class TestMergeIndexesFieldLevelVsSettings:
    """Field-level Indexed() merged with Settings indexes."""

    def test_field_indexed_and_settings_ttl_both_kept(self):
        """Indexed() produces a plain index; Settings adds TTL → both survive."""
        field_index = IndexModelField(IndexModel([("created_at", 1)]))
        settings_index = IndexModelField(
            IndexModel(
                [("created_at", 1)],
                name="ttl_idx",
                expireAfterSeconds=3600,
            )
        )

        merged = IndexModelField.merge_indexes([field_index], [settings_index])
        assert len(merged) == 2

    def test_field_indexed_and_settings_same_options_deduplicates(self):
        field_index = IndexModelField(IndexModel([("status", 1)], unique=True))
        settings_index = IndexModelField(
            IndexModel([("status", 1)], name="status_unique", unique=True)
        )

        merged = IndexModelField.merge_indexes([field_index], [settings_index])
        assert len(merged) == 1
        assert merged[0].name == "status_unique"


class TestMergeIndexesBackwardCompat:
    """Ensures existing merge_indexes behavior from inheritance is preserved."""

    def test_full_merge_scenario(self):
        """Reproduces the existing DocumentWithIndexMerging1/2 expected behavior."""
        parent_indexes = [
            IndexModelField(IndexModel([("s1", ASCENDING)])),
            IndexModelField(IndexModel([("s2", ASCENDING)])),
            IndexModelField(IndexModel([("s3", ASCENDING)], name="s3_index")),
            IndexModelField(IndexModel([("s4", ASCENDING)], name="s4_index")),
        ]
        child_indexes = [
            IndexModelField(IndexModel([("s0", ASCENDING)])),
            IndexModelField(IndexModel([("s1", ASCENDING)])),
            IndexModelField(IndexModel([("s2", DESCENDING)])),
            IndexModelField(IndexModel([("s3", DESCENDING)], name="s3_index")),
        ]

        merged = IndexModelField.merge_indexes(parent_indexes, child_indexes)

        names = {idx.name for idx in merged}
        assert "s0_1" in names
        assert "s1_1" in names
        assert "s4_index" in names
        assert "s3_index" in names
        s2_idx = next(
            idx
            for idx in merged
            if list(idx.index.document["key"].keys()) == ["s2"]
        )
        assert dict(s2_idx.index.document["key"])["s2"] == DESCENDING


class TestMergeIndexesEmptyInputs:
    def test_both_empty(self):
        assert IndexModelField.merge_indexes([], []) == []

    def test_left_empty(self):
        idx = IndexModelField(IndexModel([("a", 1)]))
        assert len(IndexModelField.merge_indexes([], [idx])) == 1

    def test_right_empty(self):
        idx = IndexModelField(IndexModel([("a", 1)]))
        assert len(IndexModelField.merge_indexes([idx], [])) == 1


class TestCanonicalOptions:
    """Tests for pre-computed _canonical_options on IndexModelField."""

    def test_dict_option_canonicalized_via_json(self):
        idx = IndexModelField(
            IndexModel(
                [("x", 1)],
                name="idx",
                partialFilterExpression={"b": 2, "a": 1},
            )
        )
        # Dict value should be a JSON string with sorted keys
        opt_dict = dict(idx._canonical_options)
        assert opt_dict["partialFilterExpression"] == '{"a": 1, "b": 2}'

    def test_primitive_options_unchanged(self):
        idx = IndexModelField(
            IndexModel([("x", 1)], name="idx", unique=True, sparse=True)
        )
        opt_dict = dict(idx._canonical_options)
        assert opt_dict["unique"] is True
        assert opt_dict["sparse"] is True

    def test_name_excluded_from_canonical(self):
        idx = IndexModelField(
            IndexModel([("x", 1)], name="my_name", unique=True)
        )
        keys = [k for k, _ in idx._canonical_options]
        assert "name" not in keys


# ---------------------------------------------------------------------------
# Integration tests: index creation with real MongoDB
# ---------------------------------------------------------------------------


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


async def test_index_recreation(settings):
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

    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await db.drop_collection("sample")

        await init_beanie(database=db, document_models=[Sample1])
        await init_beanie(
            database=db, document_models=[Sample2], allow_index_dropping=True
        )

        await db.drop_collection("sample")


async def test_index_on_custom_types(settings):
    class Sample1(Document):
        name: Indexed(Color, unique=True)

        class Settings:
            name = "sample"

    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await db.drop_collection("sample")
        await init_beanie(database=db, document_models=[Sample1])
        await db.drop_collection("sample")


async def test_merge_indexes():
    """Backward compat: inheritance-based merge still works correctly."""
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


async def test_merge_multiple_indexes_same_field_same_options(settings):
    """Identical indexes on same field collapse to one."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
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


async def test_merge_multiple_indexes_same_field_different_name_same_options(
    settings,
):
    """Same options but different explicit names → deduplicates (last wins)."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
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


async def test_merge_multiple_indexes_same_field_different_options(settings):
    """Different options on same field → both indexes created (user's bug fix)."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[DocumentWithMultipleIndexesOnSameField],
        )

        collection = (
            DocumentWithMultipleIndexesOnSameField.get_pymongo_collection()
        )
        index_info = await collection.index_information()

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


async def test_merge_compound_indexes(settings):
    """Compound indexes with different directions/options all preserved."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db, document_models=[DocumentWithCompoundIndexes]
        )

        collection = DocumentWithCompoundIndexes.get_pymongo_collection()
        index_info = await collection.index_information()

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


async def test_merge_compound_indexes_direction_conflict(settings):
    """Compound indexes differing only in direction → both kept."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[DocumentWithCompoundIndexesDirectionConflict],
        )

        collection = DocumentWithCompoundIndexesDirectionConflict.get_pymongo_collection()
        index_info = await collection.index_information()

        assert json.loads(json.dumps(index_info)) == {
            "_id_": {"v": 2, "key": [["_id", 1]]},
            "a_1_b_-1": {"v": 2, "key": [["a", 1], ["b", -1]]},
            "a_-1_b_-1": {"v": 2, "key": [["a", -1], ["b", -1]]},
        }


async def test_merge_compound_indexes_field_order_conflict(settings):
    """Compound indexes with same fields in different order → both kept."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[DocumentWithCompoundIndexesFieldOrderConflict],
        )

        collection = DocumentWithCompoundIndexesFieldOrderConflict.get_pymongo_collection()
        index_info = await collection.index_information()

        assert json.loads(json.dumps(index_info)) == {
            "_id_": {"v": 2, "key": [["_id", 1]]},
            "a_1_b_1": {"v": 2, "key": [["a", 1], ["b", 1]]},
            "b_1_a_1": {"v": 2, "key": [["b", 1], ["a", 1]]},
        }


async def test_merge_indexes_options_order_conflict(settings):
    """Options in different order are canonicalized → deduplicates."""
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        db = client[settings.mongodb_db_name]
        await init_beanie(
            database=db,
            document_models=[
                DocumentWithMultipleSameIndexesOptionOrderConflict
            ],
        )

        collection = DocumentWithMultipleSameIndexesOptionOrderConflict.get_pymongo_collection()
        index_info = await collection.index_information()

        assert json.loads(json.dumps(index_info)) == {
            "_id_": {"v": 2, "key": [["_id", 1]]},
            "a_1": {"v": 2, "key": [["a", 1]], "unique": True, "sparse": True},
        }
