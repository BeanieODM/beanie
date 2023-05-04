import pytest

from beanie.exceptions import (
    DocumentNotFound,
    ReplaceError,
)
from beanie.odm.fields import PydanticObjectId
from tests.odm.models import (
    DocumentTestModel,
    ModelWithOptionalField,
    DocumentWithKeepNullsFalse,
)


# REPLACE

#
# async def test_replace_one(document):
#     new_doc = DocumentTestModel(
#         test_int=0, test_str="REPLACED_VALUE", test_list=[]
#     )
#     await DocumentTestModel.replace_one({"_id": document.id}, new_doc)
#     new_document = await DocumentTestModel.get(document.id)
#     assert new_document.test_str == "REPLACED_VALUE"


async def test_replace_many(documents):
    await documents(10, "foo")
    created_documents = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    to_replace = []
    for document in created_documents[:5]:
        document.test_str = "REPLACED_VALUE"
        to_replace.append(document)
    await DocumentTestModel.replace_many(to_replace)

    replaced_documetns = await DocumentTestModel.find_many(
        {"test_str": "REPLACED_VALUE"}
    ).to_list()
    assert len(replaced_documetns) == 5


async def test_replace_many_not_all_the_docs_found(documents):
    await documents(10, "foo")
    created_documents = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    to_replace = []
    created_documents[0].id = PydanticObjectId()
    for document in created_documents[:5]:
        document.test_str = "REPLACED_VALUE"
        to_replace.append(document)
    with pytest.raises(ReplaceError):
        await DocumentTestModel.replace_many(to_replace)


async def test_replace(document):
    update_data = {"test_str": "REPLACED_VALUE"}
    new_doc = document.copy(update=update_data)
    # document.test_str = "REPLACED_VALUE"
    await new_doc.replace()
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_str == "REPLACED_VALUE"


async def test_replace_not_saved(document_not_inserted):
    with pytest.raises(ValueError):
        await document_not_inserted.replace()


async def test_replace_not_found(document_not_inserted):
    document_not_inserted.id = PydanticObjectId()
    with pytest.raises(DocumentNotFound):
        await document_not_inserted.replace()


# SAVE
async def test_save(document):
    update_data = {"test_str": "REPLACED_VALUE"}
    new_doc = document.copy(update=update_data)
    # document.test_str = "REPLACED_VALUE"
    await new_doc.save()
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_str == "REPLACED_VALUE"


async def test_save_not_saved(document_not_inserted):
    await document_not_inserted.save()
    assert (
        hasattr(document_not_inserted, "id")
        and document_not_inserted.id is not None
    )
    from_db = await DocumentTestModel.get(document_not_inserted.id)
    assert from_db == document_not_inserted


async def test_save_not_found(document_not_inserted):
    document_not_inserted.id = PydanticObjectId()
    await document_not_inserted.save()
    assert (
        hasattr(document_not_inserted, "id")
        and document_not_inserted.id is not None
    )
    from_db = await DocumentTestModel.get(document_not_inserted.id)
    assert from_db == document_not_inserted


# UPDATE


async def test_update_one(document):
    await DocumentTestModel.find_one(
        {"_id": document.id, "test_list.test_str": "foo"}
    ).update({"$set": {"test_list.$.test_str": "foo_foo"}})
    new_document = await DocumentTestModel.get(document.id)
    assert new_document.test_list[0].test_str == "foo_foo"


async def test_update_many(documents):
    await documents(10, "foo")
    await documents(7, "bar")
    await DocumentTestModel.find_many({"test_str": "foo"}).update(
        {"$set": {"test_str": "bar"}}
    )
    bar_documetns = await DocumentTestModel.find_many(
        {"test_str": "bar"}
    ).to_list()
    assert len(bar_documetns) == 17
    foo_documetns = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    assert len(foo_documetns) == 0


async def test_update_all(documents):
    await documents(10, "foo")
    await documents(7, "bar")
    await DocumentTestModel.update_all(
        {"$set": {"test_str": "smth_else"}},
    )
    bar_documetns = await DocumentTestModel.find_many(
        {"test_str": "bar"}
    ).to_list()
    assert len(bar_documetns) == 0
    foo_documetns = await DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    assert len(foo_documetns) == 0
    smth_else_documetns = await DocumentTestModel.find_many(
        {"test_str": "smth_else"}
    ).to_list()
    assert len(smth_else_documetns) == 17


async def test_save_keep_nulls_false():
    model = ModelWithOptionalField(i=10, s="TEST_MODEL")
    doc = DocumentWithKeepNullsFalse(m=model, o="TEST_DOCUMENT")

    await doc.insert()

    doc.o = None
    doc.m.s = None
    await doc.save()

    from_db = await DocumentWithKeepNullsFalse.get(doc.id)
    assert from_db.o is None
    assert from_db.m.s is None

    raw_data = (
        await DocumentWithKeepNullsFalse.get_motor_collection().find_one(
            {"_id": doc.id}
        )
    )
    assert raw_data == {"_id": doc.id, "m": {"i": 10}}


async def test_save_changes_keep_nulls_false():
    model = ModelWithOptionalField(i=10, s="TEST_MODEL")
    doc = DocumentWithKeepNullsFalse(m=model, o="TEST_DOCUMENT")

    await doc.insert()

    doc.o = None
    doc.m.s = None

    await doc.save_changes()

    from_db = await DocumentWithKeepNullsFalse.get(doc.id)
    assert from_db.o is None
    assert from_db.m.s is None

    raw_data = (
        await DocumentWithKeepNullsFalse.get_motor_collection().find_one(
            {"_id": doc.id}
        )
    )
    assert raw_data == {"_id": doc.id, "m": {"i": 10}}


# WITH SESSION


# async def test_update_with_session(document: DocumentTestModel, session):
#     buf_len = len(document.test_list)
#     to_insert = SubDocument(test_str="test")
#     await document.update(
#         update_query={"$push": {"test_list": to_insert.dict()}},
#         session=session,
#     )
#     new_document = await DocumentTestModel.get(document.id, session=session)
#     assert len(new_document.test_list) == buf_len + 1
#
#
# async def test_replace_one_with_session(document, session):
#     new_doc = DocumentTestModel(
#         test_int=0, test_str="REPLACED_VALUE", test_list=[]
#     )
#     await DocumentTestModel.replace_one(
#         {"_id": document.id}, new_doc, session=session
#     )
#     new_document = await DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_str == "REPLACED_VALUE"
#
#
# async def test_replace_with_session(document, session):
#     update_data = {"test_str": "REPLACED_VALUE"}
#     new_doc: DocumentTestModel = document.copy(update=update_data)
#     # document.test_str = "REPLACED_VALUE"
#     await new_doc.replace(session=session)
#     new_document = await DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_str == "REPLACED_VALUE"
#
#
# async def test_update_one_with_session(document, session):
#     await DocumentTestModel.update_one(
#         update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
#         filter_query={"_id": document.id, "test_list.test_str": "foo"},
#         session=session,
#     )
#     new_document = await DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_list[0].test_str == "foo_foo"
#
#
# async def test_update_many_with_session(documents, session):
#     await documents(10, "foo")
#     await documents(7, "bar")
#     await DocumentTestModel.update_many(
#         update_query={"$set": {"test_str": "bar"}},
#         filter_query={"test_str": "foo"},
#         session=session,
#     )
#     bar_documetns = await DocumentTestModel.find_many(
#         {"test_str": "bar"}, session=session
#     ).to_list()
#     assert len(bar_documetns) == 17
#     foo_documetns = await DocumentTestModel.find_many(
#         {"test_str": "foo"}, session=session
#     ).to_list()
#     assert len(foo_documetns) == 0
#
#
# async def test_update_all_with_session(documents, session):
#     await documents(10, "foo")
#     await documents(7, "bar")
#     await DocumentTestModel.update_all(
#         update_query={"$set": {"test_str": "smth_else"}}, session=session
#     )
#     bar_documetns = await DocumentTestModel.find_many(
#         {"test_str": "bar"}, session=session
#     ).to_list()
#     assert len(bar_documetns) == 0
#     foo_documetns = await DocumentTestModel.find_many(
#         {"test_str": "foo"}, session=session
#     ).to_list()
#     assert len(foo_documetns) == 0
#     smth_else_documetns = await DocumentTestModel.find_many(
#         {"test_str": "smth_else"}, session=session
#     ).to_list()
#     assert len(smth_else_documetns) == 17
