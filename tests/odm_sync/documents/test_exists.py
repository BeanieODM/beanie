from tests.odm_sync.models import SyncDocumentTestModel


def test_count_with_filter_query(documents):
    documents(4, "uno", True)
    documents(2, "dos", True)
    documents(1, "cuatro", True)
    e = SyncDocumentTestModel.find_many({"test_str": "dos"}).exists()
    assert e is True

    e = SyncDocumentTestModel.find_one({"test_str": "dos"}).exists()
    assert e is True

    e = SyncDocumentTestModel.find_many({"test_str": "wrong"}).exists()
    assert e is False
