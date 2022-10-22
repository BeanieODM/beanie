from tests.sync.models import DocumentTestModel


def test_count_with_filter_query(documents):
    documents(4, "uno", True)
    documents(2, "dos", True)
    documents(1, "cuatro", True)
    e = DocumentTestModel.find_many({"test_str": "dos"}).exists()
    assert e is True

    e = DocumentTestModel.find_one({"test_str": "dos"}).exists()
    assert e is True

    e = DocumentTestModel.find_many({"test_str": "wrong"}).exists()
    assert e is False
