import pytest

from beanie import Document
from beanie.exceptions import DocumentWasNotSaved, DocumentAlreadyCreated
from tests.odm.models import DocumentTestModel, DocumentWithCustomId


def test_not_inserted_doc(document_not_inserted):
    assert document_not_inserted._is_inserted is False


async def test_inserted_doc(document: Document):
    assert document._is_inserted is True


async def test_get_doc(document):
    new_doc = await DocumentTestModel.get(document.id)
    assert new_doc._is_inserted is True


async def test_find_docs(documents):
    await documents(10)
    async for doc in DocumentTestModel.find(
        DocumentTestModel.test_str == "kipasa"
    ):
        assert doc._is_inserted is True

    docs = await DocumentTestModel.find(
        DocumentTestModel.test_str == "kipasa"
    ).to_list()
    assert len(docs) > 0
    for doc in docs:
        assert doc._is_inserted is True


async def test_replace_doc_not_inserted(document_not_inserted):
    document_not_inserted.test_str = "TEST"
    with pytest.raises(DocumentWasNotSaved):
        await document_not_inserted.replace()


async def test_replace_doc(document):
    document.test_str = "TEST"
    await document.replace()
    assert document._is_inserted is True


async def test_sync_not_inserted(document_not_inserted):
    with pytest.raises(ValueError):
        await document_not_inserted._sync()


async def test_sync_doc(document):
    await document._sync()
    assert document._is_inserted is True


async def test_insert_doc(document_not_inserted):
    await document_not_inserted.insert()
    assert document_not_inserted._is_inserted is True
    with pytest.raises(DocumentAlreadyCreated):
        await document_not_inserted.insert()


async def test_custom_id():
    doc = DocumentWithCustomId(name="TEST")
    assert doc._is_inserted is False

    await doc.insert()
    assert doc._is_inserted is True

    new_doc = await DocumentWithCustomId.get(doc.id)
    assert new_doc._is_inserted is True
