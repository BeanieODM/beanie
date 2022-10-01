import pytest
from pymongo.errors import BulkWriteError

from beanie.odm_sync.bulk import BulkWriter
from beanie.odm_sync.operators.update.general import Set
from tests.odm_sync.models import SyncDocumentTestModel


def test_insert(documents_not_inserted):
    documents = documents_not_inserted(2)
    with BulkWriter() as bulk_writer:
        SyncDocumentTestModel.insert_one(documents[0], bulk_writer=bulk_writer)
        SyncDocumentTestModel.insert_one(documents[1], bulk_writer=bulk_writer)

    new_documents = SyncDocumentTestModel.find_all().to_list()
    assert len(new_documents) == 2


def test_update(documents, document_not_inserted):
    documents(5)
    doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 0
    ).run()
    doc.test_int = 100
    with BulkWriter() as bulk_writer:
        doc.save_changes(bulk_writer=bulk_writer)
        SyncDocumentTestModel.find_one(
            SyncDocumentTestModel.test_int == 1
        ).update(
            Set({SyncDocumentTestModel.test_int: 1000}),
            bulk_writer=bulk_writer,
        ).run()
        SyncDocumentTestModel.find(
            SyncDocumentTestModel.test_int < 100
        ).update(
            Set({SyncDocumentTestModel.test_int: 2000}),
            bulk_writer=bulk_writer,
        ).run()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == 100
            ).to_list()
        )
        == 1
    )
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == 1000
            ).to_list()
        )
        == 1
    )
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == 2000
            ).to_list()
        )
        == 3
    )


def test_delete(documents, document_not_inserted):
    documents(5)
    doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 0
    ).run()
    with BulkWriter() as bulk_writer:
        doc.delete(bulk_writer=bulk_writer)
        SyncDocumentTestModel.find_one(
            SyncDocumentTestModel.test_int == 1
        ).delete(bulk_writer=bulk_writer).run()
        SyncDocumentTestModel.find(SyncDocumentTestModel.test_int < 4).delete(
            bulk_writer=bulk_writer
        ).run()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 1


def test_replace(documents, document_not_inserted):
    documents(5)
    doc = SyncDocumentTestModel.find_one(
        SyncDocumentTestModel.test_int == 0
    ).run()
    doc.test_int = 100
    with BulkWriter() as bulk_writer:
        doc.replace(bulk_writer=bulk_writer)

        document_not_inserted.test_int = 100

        SyncDocumentTestModel.find_one(
            SyncDocumentTestModel.test_int == 1
        ).replace_one(document_not_inserted, bulk_writer=bulk_writer)

    assert len(SyncDocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == 100
            ).to_list()
        )
        == 2
    )


def test_upsert_find_many_not_found(documents, document_not_inserted):
    documents(5)
    document_not_inserted.test_int = -10000
    with BulkWriter() as bulk_writer:
        SyncDocumentTestModel.find(
            SyncDocumentTestModel.test_int < -1000
        ).upsert(
            {"$set": {SyncDocumentTestModel.test_int: 0}},
            on_insert=document_not_inserted,
        ).run()

        bulk_writer.commit()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 6
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == -10000
            ).to_list()
        )
        == 1
    )


def test_upsert_find_one_not_found(documents, document_not_inserted):
    documents(5)
    document_not_inserted.test_int = -10000
    with BulkWriter() as bulk_writer:
        SyncDocumentTestModel.find_one(
            SyncDocumentTestModel.test_int < -1000
        ).upsert(
            {"$set": {SyncDocumentTestModel.test_int: 0}},
            on_insert=document_not_inserted,
        ).run()

        bulk_writer.commit()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 6
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == -10000
            ).to_list()
        )
        == 1
    )


def test_upsert_find_many_found(documents, document_not_inserted):
    documents(5)
    with BulkWriter() as bulk_writer:
        SyncDocumentTestModel.find(SyncDocumentTestModel.test_int == 1).upsert(
            {"$set": {SyncDocumentTestModel.test_int: -10000}},
            on_insert=document_not_inserted,
        ).run()

        bulk_writer.commit()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == -10000
            ).to_list()
        )
        == 1
    )


def test_upsert_find_one_found(documents, document_not_inserted):
    documents(5)
    with BulkWriter() as bulk_writer:
        SyncDocumentTestModel.find_one(
            SyncDocumentTestModel.test_int == 1
        ).upsert(
            {"$set": {SyncDocumentTestModel.test_int: -10000}},
            on_insert=document_not_inserted,
        ).run()

        bulk_writer.commit()

    assert len(SyncDocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            SyncDocumentTestModel.find(
                SyncDocumentTestModel.test_int == -10000
            ).to_list()
        )
        == 1
    )


def test_internal_error(document):
    with pytest.raises(BulkWriteError):
        with BulkWriter() as bulk_writer:
            SyncDocumentTestModel.insert_one(document, bulk_writer=bulk_writer)
