from tests.odm_sync.models import SyncDocumentTestModel


def test_delete_one(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    SyncDocumentTestModel.find_one({"test_str": "uno"}).delete()
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 6


def test_delete_one_not_found(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    SyncDocumentTestModel.find_one({"test_str": "wrong"}).delete()
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 7


def test_delete_many(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    SyncDocumentTestModel.find_many({"test_str": "uno"}).delete()
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 3


def test_delete_many_not_found(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    SyncDocumentTestModel.find_many({"test_str": "wrong"}).delete()
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 7


def test_delete_all(documents):
    documents(4, "uno")
    documents(2, "dos")
    documents(1, "cuatro")
    SyncDocumentTestModel.delete_all()
    documents = SyncDocumentTestModel.find_all().to_list()
    assert len(documents) == 0


def test_delete(document):
    doc_id = document.id
    document.delete()
    new_document = SyncDocumentTestModel.get(doc_id)
    assert new_document is None
