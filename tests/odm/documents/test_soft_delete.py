from tests.odm.models import DocumentTestModelWithSoftDelete


async def test_insert_one_and_delete_one(document_soft_delete_not_inserted):
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

    # check if document exist
    document = await DocumentTestModelWithSoftDelete.get(document_id=result.id)

    assert document is None


async def test_find_many(documents_soft_delete_not_inserted):
    # insert 2 documents
    item_1 = await documents_soft_delete_not_inserted[0].insert()
    item_2 = await documents_soft_delete_not_inserted[1].insert()

    # use `.find_many()` to get them all
    results = await DocumentTestModelWithSoftDelete.find_many().to_list()
    assert len(results) == 2

    # delete one of them
    await item_1.delete()

    results = await DocumentTestModelWithSoftDelete.find_many().to_list()

    assert len(results) == 1
    assert results[0].id == item_2.id
