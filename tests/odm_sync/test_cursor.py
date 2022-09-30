from tests.odm_sync.models import SyncDocumentTestModel


def test_to_list(documents):
    documents(10)
    result = SyncDocumentTestModel.find_all().to_list()
    assert len(result) == 10


def test_async_for(documents):
    documents(10)
    for document in SyncDocumentTestModel.find_all():
        assert document.test_int in list(range(10))
