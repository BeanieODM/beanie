import pytest
from pymongo.errors import DuplicateKeyError

from beanie.odm.fields import PydanticObjectId
from tests.odm.models import (
    DocumentTestModel,
    ModelWithOptionalField,
    DocumentWithKeepNullsFalse,
)


async def test_insert_one(document_not_inserted):
    result = await DocumentTestModel.insert_one(document_not_inserted)
    document = await DocumentTestModel.get(result.id)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


async def test_insert_many(documents_not_inserted):
    await DocumentTestModel.insert_many(documents_not_inserted(10))
    documents = await DocumentTestModel.find_all().to_list()
    assert len(documents) == 10


async def test_create(document_not_inserted):
    await document_not_inserted.insert()
    assert isinstance(document_not_inserted.id, PydanticObjectId)


async def test_create_twice(document_not_inserted):
    await document_not_inserted.insert()
    with pytest.raises(DuplicateKeyError):
        await document_not_inserted.insert()


async def test_insert_one_with_session(document_not_inserted, session):
    result = await DocumentTestModel.insert_one(
        document_not_inserted, session=session
    )
    document = await DocumentTestModel.get(result.id, session=session)
    assert document is not None
    assert document.test_int == document_not_inserted.test_int
    assert document.test_list == document_not_inserted.test_list
    assert document.test_str == document_not_inserted.test_str


async def test_insert_many_with_session(documents_not_inserted, session):
    await DocumentTestModel.insert_many(
        documents_not_inserted(10), session=session
    )
    documents = await DocumentTestModel.find_all(session=session).to_list()
    assert len(documents) == 10


async def test_create_with_session(document_not_inserted, session):
    await document_not_inserted.insert(session=session)
    assert isinstance(document_not_inserted.id, PydanticObjectId)


async def test_insert_keep_nulls_false():
    model = ModelWithOptionalField(i=10)
    doc = DocumentWithKeepNullsFalse(m=model)

    await doc.insert()

    new_doc = await DocumentWithKeepNullsFalse.get(doc.id)

    assert new_doc.m.i == 10
    assert new_doc.m.s is None
    assert new_doc.o is None

    raw_data = (
        await DocumentWithKeepNullsFalse.get_motor_collection().find_one(
            {"_id": doc.id}
        )
    )
    assert raw_data == {
        "_id": doc.id,
        "m": {"i": 10},
    }


async def test_insert_many_keep_nulls_false():
    models = [ModelWithOptionalField(i=10), ModelWithOptionalField(i=11)]
    docs = [DocumentWithKeepNullsFalse(m=m) for m in models]

    await DocumentWithKeepNullsFalse.insert_many(docs)

    new_docs = await DocumentWithKeepNullsFalse.find_all().to_list()

    assert len(new_docs) == 2

    assert new_docs[0].m.i == 10
    assert new_docs[0].m.s is None
    assert new_docs[0].o is None

    assert new_docs[1].m.i == 11
    assert new_docs[1].m.s is None
    assert new_docs[1].o is None

    raw_data = (
        await DocumentWithKeepNullsFalse.get_motor_collection().find_one(
            {"_id": new_docs[0].id}
        )
    )
    assert raw_data == {
        "_id": new_docs[0].id,
        "m": {"i": 10},
    }
    raw_data = (
        await DocumentWithKeepNullsFalse.get_motor_collection().find_one(
            {"_id": new_docs[1].id}
        )
    )
    assert raw_data == {
        "_id": new_docs[1].id,
        "m": {"i": 11},
    }
