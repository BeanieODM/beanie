from tests.odm.models import DocumentTestModel


async def test_delete_one(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.find_one({"test_str": "uno"}).delete()
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 6


async def test_delete_one_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.find_one({"test_str": "wrong"}).delete()
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 7


async def test_delete_many(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.find_many({"test_str": "uno"}).delete()
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 3


async def test_delete_many_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.find_many({"test_str": "wrong"}).delete()
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 7


async def test_delete_all(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_all()
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 0


async def test_delete(document):
    doc_id = document.id
    await document.delete()
    new_document = await DocumentTestModel.get(doc_id)
    assert new_document is None
