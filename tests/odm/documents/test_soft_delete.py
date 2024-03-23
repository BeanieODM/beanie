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
