import pytest
from pymongo.errors import BulkWriteError

from beanie.odm.bulk import BulkWriter
from beanie.odm.operators.update.general import Set
from tests.odm.models import DocumentTestModel


async def test_insert(documents_not_inserted):
    documents = documents_not_inserted(2)
    async with BulkWriter() as bulk_writer:
        await DocumentTestModel.insert_one(
            documents[0], bulk_writer=bulk_writer
        )
        await DocumentTestModel.insert_one(
            documents[1], bulk_writer=bulk_writer
        )

    new_documents = await DocumentTestModel.find_all().to_list()
    assert len(new_documents) == 2


async def test_update(documents, document_not_inserted):
    await documents(5)
    doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 0)
    doc.test_int = 100
    async with BulkWriter() as bulk_writer:
        await doc.save_changes(bulk_writer=bulk_writer)
        await DocumentTestModel.find_one(
            DocumentTestModel.test_int == 1
        ).update(
            Set({DocumentTestModel.test_int: 1000}), bulk_writer=bulk_writer
        )
        await DocumentTestModel.find(DocumentTestModel.test_int < 100).update(
            Set({DocumentTestModel.test_int: 2000}), bulk_writer=bulk_writer
        )

    assert len(await DocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            await DocumentTestModel.find(
                DocumentTestModel.test_int == 100
            ).to_list()
        )
        == 1
    )
    assert (
        len(
            await DocumentTestModel.find(
                DocumentTestModel.test_int == 1000
            ).to_list()
        )
        == 1
    )
    assert (
        len(
            await DocumentTestModel.find(
                DocumentTestModel.test_int == 2000
            ).to_list()
        )
        == 3
    )


async def test_delete(documents, document_not_inserted):
    await documents(5)
    doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 0)
    async with BulkWriter() as bulk_writer:
        await doc.delete(bulk_writer=bulk_writer)
        await DocumentTestModel.find_one(
            DocumentTestModel.test_int == 1
        ).delete(bulk_writer=bulk_writer)
        await DocumentTestModel.find(DocumentTestModel.test_int < 4).delete(
            bulk_writer=bulk_writer
        )

    assert len(await DocumentTestModel.find_all().to_list()) == 1


async def test_replace(documents, document_not_inserted):
    await documents(5)
    doc = await DocumentTestModel.find_one(DocumentTestModel.test_int == 0)
    doc.test_int = 100
    async with BulkWriter() as bulk_writer:
        await doc.replace(bulk_writer=bulk_writer)

        document_not_inserted.test_int = 100

        await DocumentTestModel.find_one(
            DocumentTestModel.test_int == 1
        ).replace_one(document_not_inserted, bulk_writer=bulk_writer)

    assert len(await DocumentTestModel.find_all().to_list()) == 5
    assert (
        len(
            await DocumentTestModel.find(
                DocumentTestModel.test_int == 100
            ).to_list()
        )
        == 2
    )


async def test_internal_error(document):
    with pytest.raises(BulkWriteError):
        async with BulkWriter() as bulk_writer:
            await DocumentTestModel.insert_one(
                document, bulk_writer=bulk_writer
            )
