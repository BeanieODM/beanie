import pymongo

from beanie.odm.fields import PydanticObjectId
from tests.odm.models import DocumentTestModel


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


async def test_find_all_limit(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_all(limit=5).to_list()
    assert len(result) == 5


async def test_find_all_skip(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_all(skip=1).to_list()
    assert len(result) == 6


async def test_find_all_sort(documents):
    await documents(4, "uno", True)
    await documents(2, "dos", True)
    await documents(1, "cuatro", True)
    result = await DocumentTestModel.find_all(
        sort=[
            ("test_str", pymongo.ASCENDING),
            ("test_int", pymongo.DESCENDING),
        ]
    ).to_list()
    assert result[0].test_str == "cuatro"
    assert result[1].test_str == result[2].test_str == "dos"
    assert (
        result[3].test_str
        == result[4].test_str
        == result[5].test_str
        == result[5].test_str
        == "uno"
    )

    assert result[1].test_int >= result[2].test_int
    assert (
        result[3].test_int
        >= result[4].test_int
        >= result[5].test_int
        >= result[6].test_int
    )


async def test_find_many(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many(
        DocumentTestModel.test_str == "uno"
    ).to_list()
    assert len(result) == 4


async def test_find_many_limit(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many(
        {"test_str": "uno"}, limit=2
    ).to_list()
    assert len(result) == 2


async def test_find_many_skip(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many(
        {"test_str": "uno"}, skip=1
    ).to_list()
    assert len(result) == 3


async def test_find_many_sort(documents):
    await documents(4, "uno", True)
    await documents(2, "dos", True)
    await documents(1, "cuatro", True)
    result = await DocumentTestModel.find_many(
        {"test_str": "uno"}, sort="test_int"
    ).to_list()
    assert (
        result[0].test_int
        <= result[1].test_int
        <= result[2].test_int
        <= result[3].test_int
    )

    result = await DocumentTestModel.find_many(
        {"test_str": "uno"}, sort=[("test_int", pymongo.DESCENDING)]
    ).to_list()
    assert (
        result[0].test_int
        >= result[1].test_int
        >= result[2].test_int
        >= result[3].test_int
    )


async def test_find_many_not_found(documents):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many({"test_str": "wrong"}).to_list()
    assert len(result) == 0


async def test_get_with_session(document, session):
    new_document = await DocumentTestModel.get(document.id, session=session)
    assert new_document == document


async def test_find_one_with_session(documents, session):
    inserted_one = await documents(1, "kipasa")
    await documents(10, "smthe else")

    expected_doc_id = PydanticObjectId(inserted_one[0])

    new_document = await DocumentTestModel.find_one(
        {"test_str": "kipasa"}, session=session
    )
    assert new_document.id == expected_doc_id


async def test_find_all_with_session(documents, session):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_all(session=session).to_list()
    assert len(result) == 7


async def test_find_many_with_session(documents, session):
    await documents(4, "uno")
    await documents(2, "dos")
    await documents(1, "cuatro")
    result = await DocumentTestModel.find_many(
        {"test_str": "uno"}, session=session
    ).to_list()
    assert len(result) == 4
