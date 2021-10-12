from tests.odm.models import DocumentTestModel


async def test_count_with_filter_query(documents):
    await documents(4, "uno", True)
    await documents(2, "dos", True)
    await documents(1, "cuatro", True)
    e = await DocumentTestModel.find_many({"test_str": "dos"}).exists()
    assert e is True

    e = await DocumentTestModel.find_one({"test_str": "dos"}).exists()
    assert e is True

    e = await DocumentTestModel.find_many({"test_str": "wrong"}).exists()
    assert e is False
