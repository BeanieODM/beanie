from tests.odm.models import DocumentTestModel


async def test_count(documents):
    await documents(4, "uno", True)
    c = await DocumentTestModel.count()
    assert c == 4


async def test_count_with_filter_query(documents):
    await documents(4, "uno", True)
    await documents(2, "dos", True)
    await documents(1, "cuatro", True)
    c = await DocumentTestModel.find_many({"test_str": "dos"}).count()
    assert c == 2


async def test_count_with_limit(documents):
    await documents(5, "five", True)
    c = await DocumentTestModel.find_all().limit(1).count()
    assert c == 1
    d = await DocumentTestModel.find_all().count()
    assert d == 5
