"""Tests for lazy initialization (init_beanie with lazy=True).

Covers:
- buildInfo caching (single call per Initializer)
- metadata caching across repeated init_beanie calls
- DocsRegistry caching
- lazy=True skips indexes
- lazy=True skips view recreation
- Document.ensure_indexes() on-demand index creation
- View.ensure_view() on-demand view materialization
- CRUD operations work after lazy init
- re-init with lazy=True reuses metadata but rebinds database
- standard (non-lazy) init still works as before
"""

from unittest.mock import patch

import pymongo
import pytest

from beanie.odm.registry import DocsRegistry
from beanie.odm.utils.init import Initializer, init_beanie
from tests.odm.models import (
    DocumentTestModel,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithSimpleIndex,
    SubDocument,
)
from tests.odm.views import ViewForTest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def _cleanup_lazy_flags():
    """Reset metadata caching flags after each test."""
    yield
    # Reset _metadata_initialized on all test classes to avoid leaking
    # state between tests.
    for cls in [
        DocumentTestModel,
        DocumentTestModelWithCustomCollectionName,
        DocumentTestModelWithSimpleIndex,
        ViewForTest,
    ]:
        if hasattr(cls, "_metadata_initialized"):
            cls._metadata_initialized = False


LAZY_MODELS = [
    DocumentTestModel,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithSimpleIndex,
    ViewForTest,
]


# ---------------------------------------------------------------------------
# Phase 1: buildInfo caching
# ---------------------------------------------------------------------------


class TestBuildInfoCaching:
    async def test_single_build_info_call(self, db):
        """buildInfo should be called exactly once per Initializer,
        regardless of how many document models are initialized."""
        original_command = db.command

        call_count = 0

        async def counting_command(cmd, *args, **kwargs):
            nonlocal call_count
            if isinstance(cmd, dict) and "buildInfo" in cmd:
                call_count += 1
            return await original_command(cmd, *args, **kwargs)

        with patch.object(db, "command", side_effect=counting_command):
            await init_beanie(
                database=db,
                document_models=LAZY_MODELS,
            )

        # Only one buildInfo call, not one per document model
        assert call_count == 1

    async def test_mongo_version_cached_on_initializer(self, db):
        """The Initializer instance should cache the MongoDB version."""
        init = Initializer(
            database=db,
            document_models=LAZY_MODELS,
        )
        # Before awaiting, no version cached
        assert init._mongo_version is None

        version = await init.get_mongo_version()
        assert isinstance(version, int)
        assert version >= 4

        # Subsequent call returns same value without DB hit
        version2 = await init.get_mongo_version()
        assert version2 == version


# ---------------------------------------------------------------------------
# Phase 1: Metadata caching
# ---------------------------------------------------------------------------


class TestMetadataCaching:
    async def test_metadata_initialized_flag_set(self, db):
        """After init_beanie, _metadata_initialized should be True
        on each document class."""
        await init_beanie(
            database=db,
            document_models=LAZY_MODELS,
        )
        for cls in LAZY_MODELS:
            assert getattr(cls, "_metadata_initialized", False) is True

    async def test_second_init_skips_metadata(self, db):
        """Calling init_beanie twice should skip pure-Python metadata
        work on the second call."""
        await init_beanie(
            database=db,
            document_models=LAZY_MODELS,
        )

        # Tag the settings to detect re-creation
        marker = object()
        DocumentTestModel._document_settings._test_marker = marker  # type: ignore[attr-defined]

        await init_beanie(
            database=db,
            document_models=LAZY_MODELS,
        )

        # Settings object should NOT have been replaced
        assert (
            getattr(DocumentTestModel._document_settings, "_test_marker", None)
            is marker
        )

    async def test_docs_registry_additive(self, db):
        """fill_docs_registry should add to the registry without replacing."""
        await init_beanie(
            database=db,
            document_models=LAZY_MODELS,
        )

        original_len = len(DocsRegistry._registry)

        await init_beanie(
            database=db,
            document_models=LAZY_MODELS,
        )

        # Registry should not have been wiped and re-filled from scratch
        assert len(DocsRegistry._registry) == original_len


# ---------------------------------------------------------------------------
# Phase 2: Lazy mode
# ---------------------------------------------------------------------------


class TestLazyMode:
    async def test_lazy_skips_indexes(self, db):
        """With lazy=True, no indexes (except _id) should be created."""
        # Drop everything first
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )

        # Insert a doc to force collection creation, then check indexes
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="idx_test",
        ).insert()

        indexes = await col.index_information()
        # Only the default _id index
        assert list(indexes.keys()) == ["_id_"]

    async def test_lazy_implies_skip_indexes(self, db):
        """lazy=True should force skip_indexes=True."""
        init = Initializer(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )
        assert init.skip_indexes is True

    async def test_lazy_disables_recreate_views(self, db):
        """lazy=True should force recreate_views=False."""
        init = Initializer(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
            recreate_views=True,
        )
        assert init.recreate_views is False

    async def test_crud_after_lazy_init(self, db):
        """Basic CRUD should work after lazy init."""
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        doc = DocumentTestModel(
            test_int=42,
            test_list=[SubDocument(test_str="bar")],
            test_doc=SubDocument(test_str="foo"),
            test_str="lazy_test",
        )
        await doc.insert()

        fetched = await DocumentTestModel.get(doc.id)
        assert fetched is not None
        assert fetched.test_int == 42
        assert fetched.test_str == "lazy_test"

        await fetched.delete()
        # DocumentTestModel has use_cache=True, so bypass the cache
        # by querying pymongo directly.
        raw = await DocumentTestModel.get_pymongo_collection().find_one(
            {"_id": doc.id}
        )
        assert raw is None

    async def test_expression_fields_work_after_lazy(self, db):
        """ExpressionField-based queries should work after lazy init."""
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        doc = DocumentTestModel(
            test_int=99,
            test_list=[SubDocument(test_str="x")],
            test_doc=SubDocument(test_str="y"),
            test_str="expr_test",
        )
        await doc.insert()

        results = await DocumentTestModel.find(
            DocumentTestModel.test_int == 99
        ).to_list()
        assert len(results) == 1
        assert results[0].test_str == "expr_test"

    async def test_find_all_after_lazy(self, db):
        """find_all should work after lazy init."""
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        for i in range(5):
            await DocumentTestModel(
                test_int=i,
                test_list=[SubDocument(test_str="x")],
                test_doc=SubDocument(test_str="y"),
                test_str=f"item_{i}",
            ).insert()

        all_docs = await DocumentTestModel.find_all().to_list()
        assert len(all_docs) == 5


# ---------------------------------------------------------------------------
# Phase 2: ensure_indexes / ensure_view
# ---------------------------------------------------------------------------


class TestEnsureIndexes:
    async def test_ensure_indexes_creates_indexes(self, db):
        """Document.ensure_indexes() should create declared indexes."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )

        # Insert a doc to force collection creation
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="idx_test",
        ).insert()

        # No custom indexes yet
        indexes_before = await col.index_information()
        assert len(indexes_before) == 1  # only _id

        await DocumentTestModelWithSimpleIndex.ensure_indexes()

        indexes_after = await col.index_information()
        # Should now have _id + at least one custom index
        assert len(indexes_after) > 1

    async def test_ensure_indexes_idempotent(self, db):
        """Calling ensure_indexes twice should not error."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )

        # Insert a doc to force collection creation
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="idx_test",
        ).insert()

        await DocumentTestModelWithSimpleIndex.ensure_indexes()
        count_first = len(await col.index_information())

        await DocumentTestModelWithSimpleIndex.ensure_indexes()
        count_second = len(await col.index_information())

        assert count_first == count_second

    async def test_ensure_indexes_with_allow_dropping(self, db):
        """ensure_indexes(allow_dropping=True) should drop unknown indexes."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )

        # Insert a doc to force collection creation
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="idx_test",
        ).insert()

        # Manually create an extra index
        await col.create_index([("extra_field", pymongo.ASCENDING)])

        await DocumentTestModelWithSimpleIndex.ensure_indexes(
            allow_dropping=True
        )

        indexes_after = await col.index_information()
        # The extra index should have been dropped, declared ones created.
        assert "extra_field_1" not in indexes_after
        # Declared indexes should be present
        assert "test_int_1" in indexes_after


class TestEnsureView:
    async def test_ensure_view_creates_view(self, db):
        """View.ensure_view() should create the MongoDB view."""
        # Set up source collection first
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        # Drop the view if it exists
        view_name = ViewForTest.get_settings().name
        collection_names = await db.list_collection_names()
        if view_name in collection_names:
            await db.drop_collection(view_name)

        # Init view with lazy
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel, ViewForTest],
            lazy=True,
        )

        # Now explicitly ensure the view
        await ViewForTest.ensure_view()

        collection_names = await db.list_collection_names()
        assert view_name in collection_names

    async def test_ensure_view_replaces_existing(self, db):
        """ensure_view() should drop and recreate an existing view."""
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel, ViewForTest],
            lazy=True,
        )

        # Create a dummy view manually
        view_name = ViewForTest.get_settings().name
        collection_names = await db.list_collection_names()
        if view_name in collection_names:
            await db.drop_collection(view_name)

        await db.command(
            {
                "create": view_name,
                "viewOn": "DocumentTestModel",
                "pipeline": [],
            }
        )

        # Now call ensure_view to replace it with correct pipeline
        await ViewForTest.ensure_view()

        # Verify the view works correctly (original pipeline)
        await DocumentTestModel(
            test_int=100,
            test_list=[SubDocument(test_str="x")],
            test_doc=SubDocument(test_str="y"),
            test_str="view_test",
        ).insert()

        results = await ViewForTest.all().to_list()
        # test_int=100 > 8 so it should be in the view
        found = [r for r in results if r.number == 100]
        assert len(found) == 1
        assert found[0].string == "view_test"


# ---------------------------------------------------------------------------
# Re-init scenarios
# ---------------------------------------------------------------------------


class TestReinit:
    async def test_lazy_then_full_init(self, db):
        """Going from lazy to full should create indexes."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )

        # Insert to force collection creation
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="test",
        ).insert()
        assert len(await col.index_information()) == 1  # only _id

        # Full init — indexes created
        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
        )
        assert len(await col.index_information()) > 1

    async def test_full_then_lazy_preserves_indexes(self, db):
        """A lazy re-init should not destroy existing indexes."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        # Full init — indexes created
        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
        )
        index_count = len(await col.index_information())
        assert index_count > 1

        # Lazy re-init — indexes should remain
        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            lazy=True,
        )
        assert len(await col.index_information()) == index_count

    async def test_lazy_rebinds_database(self, db):
        """Multiple lazy inits should update database/collection refs."""
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        # Collection should point to the right DB
        col = DocumentTestModel.get_pymongo_collection()
        assert col is not None
        assert col.name == "DocumentTestModel"

        # Re-init — should still work
        await init_beanie(
            database=db,
            document_models=[DocumentTestModel],
            lazy=True,
        )

        doc = DocumentTestModel(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_doc=SubDocument(test_str="y"),
            test_str="rebind_test",
        )
        await doc.insert()

        fetched = await DocumentTestModel.get(doc.id)
        assert fetched is not None
        assert fetched.test_str == "rebind_test"


# ---------------------------------------------------------------------------
# Default (non-lazy) behavior unchanged
# ---------------------------------------------------------------------------


class TestNonLazyUnchanged:
    async def test_default_creates_indexes(self, db):
        """Default init_beanie (no lazy) should create indexes as before."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
        )

        indexes = await col.index_information()
        assert len(indexes) > 1

    async def test_skip_indexes_still_works(self, db):
        """skip_indexes=True without lazy should still skip indexes."""
        col = db[DocumentTestModelWithSimpleIndex.__name__]
        await col.drop()

        await init_beanie(
            database=db,
            document_models=[DocumentTestModelWithSimpleIndex],
            skip_indexes=True,
        )

        # Insert to force collection creation
        await DocumentTestModelWithSimpleIndex(
            test_int=1,
            test_list=[SubDocument(test_str="x")],
            test_str="test",
        ).insert()

        indexes = await col.index_information()
        assert list(indexes.keys()) == ["_id_"]
