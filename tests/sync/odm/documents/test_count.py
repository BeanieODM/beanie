from tests.sync.models import DocumentTestModel


def test_count(documents):
    documents(4, "uno", True)
    c = DocumentTestModel.count()
    assert c == 4


def test_count_with_filter_query(documents):
    documents(4, "uno", True)
    documents(2, "dos", True)
    documents(1, "cuatro", True)
    c = DocumentTestModel.find_many({"test_str": "dos"}).count()
    assert c == 2
