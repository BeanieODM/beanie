from tests.odm.models import DocumentTestModel


async def test_count(documents):
    await documents(4, "uno", random=True)
    c = await DocumentTestModel.count()
    assert c == 4


async def test_count_with_filter_query(documents):
    await documents(4, "uno", random=True)
    await documents(2, "dos", random=True)
    await documents(1, "cuatro", random=True)
    c = await DocumentTestModel.find_many({"test_str": "dos"}).count()
    assert c == 2


async def test_count_with_filter_query_and_linked_document(
    documents, document
):
    await documents(4, "uno", document, random=True)
    await documents(1, "dos", random=True)
    await documents(1, "cuatro", random=True)

    c = await DocumentTestModel.find_many(
        DocumentTestModel.test_str == document.test_str
    ).count()
    assert c == 1
