from beanie.fields import PydanticObjectId
from tests.models import DocumentTestModel


async def test_get(document):
    new_document = await DocumentTestModel.get(document.id)
    assert new_document == document


async def test_get_not_found(document):
    new_document = await DocumentTestModel.get(PydanticObjectId())
    assert new_document is None


async def test_find_one(documents):
    inserted_one = await documents(1, "kipasa")
    await documents(10, "smthe else")

    expected_doc_id = PydanticObjectId(inserted_one[0])

    new_document = await DocumentTestModel.find_one({"test_str": "kipasa"})
    assert new_document.id == expected_doc_id


async def test_find_one_not_found(documents):
    await documents(10, "smthe else")

    new_document = await DocumentTestModel.find_one({"test_str": "wrong"})
    assert new_document is None


async def test_find_one_more_than_one_found(documents):
    await documents(10, "one")
    await documents(10, "two")
    new_document = await DocumentTestModel.find_one({"test_str": "one"})
    assert new_document.test_str == "one"


async def test_find_all(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_all().to_list()
    assert len(result) == 7


async def test_find_many(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many({"test_str": "uno"}).to_list()
    assert len(result) == 4


async def test_find_many_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many({"test_str": "wrong"}).to_list()
    assert len(result) == 0
