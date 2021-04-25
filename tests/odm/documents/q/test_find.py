from tests.odm.models import DocumentTestModel


async def test_find_many(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = (
        await DocumentTestModel.q()
        .find_many(DocumentTestModel.test_str == "uno")()
        .to_list()
    )
    print(result)
    assert len(result) == 4
