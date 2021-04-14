from tests.odm.models import DocumentTestModel


async def test_to_list(documents):
    await documents(10)
    result = await DocumentTestModel.find_all().to_list()
    assert len(result) == 10


async def test_async_for(documents):
    await documents(10)
    async for document in DocumentTestModel.find_all():
        assert document.test_int in list(range(10))
