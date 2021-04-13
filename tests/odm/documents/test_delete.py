from tests.odm.models import DocumentTestModel


async def test_delete_one(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_one({"test_str": "uno"})
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 6


async def test_delete_one_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_one({"test_str": "wrong"})
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 7


async def test_delete_many(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_many({"test_str": "uno"})
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 3


async def test_delete_many_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_many({"test_str": "wrong"})
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


async def test_delete_one_with_session(documents, session):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_one({"test_str": "uno"}, session=session)
    documents = await DocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 6


async def test_delete_many_with_session(documents, session):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    await DocumentTestModel.delete_many({"test_str": "uno"}, session=session)
    documents = await DocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 3


async def test_delete_with_session(document, session):
    doc_id = document.id
    await document.delete(session=session)
    new_document = await DocumentTestModel.get(doc_id, session=session)
    assert new_document is None
