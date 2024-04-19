from tests.odm.models import DocumentTestModelWithSoftDelete


async def test_get_item(document_soft_delete_not_inserted):
    # insert a document with soft delete
    result = await document_soft_delete_not_inserted.insert()

    # get from db by id
    document = await DocumentTestModelWithSoftDelete.get(document_id=result.id)

    assert document.is_deleted() is False
    assert document.deleted_at is None
    assert document.test_int == result.test_int
    assert document.test_str == result.test_str

    # # delete the document
    await document.delete()
    assert document.is_deleted() is True

    # check if document exist with `.get()`
    document = await DocumentTestModelWithSoftDelete.get(document_id=result.id)
    assert document is None

    # check document exist in trashed
    results = (
        await DocumentTestModelWithSoftDelete.find_many_in_all().to_list()
    )
    assert len(results) == 1


async def test_find_one(document_soft_delete_not_inserted):
    result = await document_soft_delete_not_inserted.insert()

    # # delete the document
    await result.delete()

    # check if document exist with `.find_one()`
    document = await DocumentTestModelWithSoftDelete.find_one(
        DocumentTestModelWithSoftDelete.id == result.id
    )
    assert document is None


async def test_find(documents_soft_delete_not_inserted):
    # insert 3 documents
    inserted_docs = []
    for doc in documents_soft_delete_not_inserted:
        result = await doc.insert()
        inserted_docs.append(result)

    # use `.find_many()` to get them all
    results = await DocumentTestModelWithSoftDelete.find().to_list()
    assert len(results) == 3

    # delete one of them
    await inserted_docs[0].delete()

    # check items in with `.find_many()`
    results = await DocumentTestModelWithSoftDelete.find_many().to_list()

    assert len(results) == 2

    founded_documents_id = [doc.id for doc in results]
    assert inserted_docs[0].id not in founded_documents_id

    # check in trashed items
    results = (
        await DocumentTestModelWithSoftDelete.find_many_in_all().to_list()
    )
    assert len(results) == 3


async def test_find_many(documents_soft_delete_not_inserted):
    # insert 2 documents
    item_1 = await documents_soft_delete_not_inserted[0].insert()
    item_2 = await documents_soft_delete_not_inserted[1].insert()

    # use `.find_many()` to get them all
    results = await DocumentTestModelWithSoftDelete.find_many().to_list()
    assert len(results) == 2

    # delete one of them
    await item_1.delete()

    # check items in with `.find_many()`
    results = await DocumentTestModelWithSoftDelete.find_many().to_list()

    assert len(results) == 1
    assert results[0].id == item_2.id

    # check in trashed items
    results = (
        await DocumentTestModelWithSoftDelete.find_many_in_all().to_list()
    )
    assert len(results) == 2


async def test_hard_delete(document_soft_delete_not_inserted):
    result = await document_soft_delete_not_inserted.insert()
    await result.hard_delete()

    # check items in with `.find_many()`
    results = await DocumentTestModelWithSoftDelete.find_many().to_list()
    assert len(results) == 0

    # check in trashed
    results = (
        await DocumentTestModelWithSoftDelete.find_many_in_all().to_list()
    )
    assert len(results) == 0
