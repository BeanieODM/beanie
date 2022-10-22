from tests.sync.models import DocumentTestModel


def test_to_list(documents):
    documents(10)
    result = DocumentTestModel.find_all().to_list()
    assert len(result) == 10


def test_async_for(documents):
    documents(10)
    for document in DocumentTestModel.find_all():
        assert document.test_int in list(range(10))
