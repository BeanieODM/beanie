import pytest

from beanie.exceptions import (
    DocumentNotFound,
    ReplaceError,
)
from beanie.odm.fields import PydanticObjectId
from tests.sync.models import DocumentTestModel


# REPLACE

#
# def test_replace_one(document):
#     new_doc = DocumentTestModel(
#         test_int=0, test_str="REPLACED_VALUE", test_list=[]
#     )
#     DocumentTestModel.replace_one({"_id": document.id}, new_doc)
#     new_document = DocumentTestModel.get(document.id)
#     assert new_document.test_str == "REPLACED_VALUE"


def test_replace_many(documents):
    documents(10, "foo")
    created_documents = DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    to_replace = []
    for document in created_documents[:5]:
        document.test_str = "REPLACED_VALUE"
        to_replace.append(document)
    DocumentTestModel.replace_many(to_replace)

    replaced_documetns = DocumentTestModel.find_many(
        {"test_str": "REPLACED_VALUE"}
    ).to_list()
    assert len(replaced_documetns) == 5


def test_replace_many_not_all_the_docs_found(documents):
    documents(10, "foo")
    created_documents = DocumentTestModel.find_many(
        {"test_str": "foo"}
    ).to_list()
    to_replace = []
    created_documents[0].id = PydanticObjectId()
    for document in created_documents[:5]:
        document.test_str = "REPLACED_VALUE"
        to_replace.append(document)
    with pytest.raises(ReplaceError):
        DocumentTestModel.replace_many(to_replace)


def test_replace(document):
    update_data = {"test_str": "REPLACED_VALUE"}
    new_doc = document.copy(update=update_data)
    # document.test_str = "REPLACED_VALUE"
    new_doc.replace()
    new_document = DocumentTestModel.get(document.id).run()
    assert new_document.test_str == "REPLACED_VALUE"


def test_replace_not_saved(document_not_inserted):
    with pytest.raises(ValueError):
        document_not_inserted.replace()


def test_replace_not_found(document_not_inserted):
    document_not_inserted.id = PydanticObjectId()
    with pytest.raises(DocumentNotFound):
        document_not_inserted.replace()


# SAVE
def test_save(document):
    update_data = {"test_str": "REPLACED_VALUE"}
    new_doc = document.copy(update=update_data)
    # document.test_str = "REPLACED_VALUE"
    new_doc.save()
    new_document = DocumentTestModel.get(document.id).run()
    assert new_document.test_str == "REPLACED_VALUE"


def test_save_not_saved(document_not_inserted):
    document_not_inserted.save()
    assert (
        hasattr(document_not_inserted, "id")
        and document_not_inserted.id is not None
    )
    from_db = DocumentTestModel.get(document_not_inserted.id).run()
    assert from_db == document_not_inserted


def test_save_not_found(document_not_inserted):
    document_not_inserted.id = PydanticObjectId()
    document_not_inserted.save()
    assert (
        hasattr(document_not_inserted, "id")
        and document_not_inserted.id is not None
    )
    from_db = DocumentTestModel.get(document_not_inserted.id).run()
    assert from_db == document_not_inserted


# UPDATE


def test_update_one(document):
    DocumentTestModel.find_one(
        {"_id": document.id, "test_list.test_str": "foo"}
    ).update({"$set": {"test_list.$.test_str": "foo_foo"}}).run()
    new_document = DocumentTestModel.get(document.id).run()
    assert new_document.test_list[0].test_str == "foo_foo"


def test_update_many(documents):
    documents(10, "foo")
    documents(7, "bar")
    DocumentTestModel.find_many({"test_str": "foo"}).update(
        {"$set": {"test_str": "bar"}}
    ).run()
    bar_documetns = DocumentTestModel.find_many({"test_str": "bar"}).to_list()
    assert len(bar_documetns) == 17
    foo_documetns = DocumentTestModel.find_many({"test_str": "foo"}).to_list()
    assert len(foo_documetns) == 0


def test_update_all(documents):
    documents(10, "foo")
    documents(7, "bar")
    DocumentTestModel.update_all(
        {"$set": {"test_str": "smth_else"}},
    ).run()
    bar_documetns = DocumentTestModel.find_many({"test_str": "bar"}).to_list()
    assert len(bar_documetns) == 0
    foo_documetns = DocumentTestModel.find_many({"test_str": "foo"}).to_list()
    assert len(foo_documetns) == 0
    smth_else_documetns = DocumentTestModel.find_many(
        {"test_str": "smth_else"}
    ).to_list()
    assert len(smth_else_documetns) == 17


# WITH SESSION


# def test_update_with_session(document: DocumentTestModel, session):
#     buf_len = len(document.test_list)
#     to_insert = SubDocument(test_str="test")
#     document.update(
#         update_query={"$push": {"test_list": to_insert.dict()}},
#         session=session,
#     )
#     new_document = DocumentTestModel.get(document.id, session=session)
#     assert len(new_document.test_list) == buf_len + 1
#
#
# def test_replace_one_with_session(document, session):
#     new_doc = DocumentTestModel(
#         test_int=0, test_str="REPLACED_VALUE", test_list=[]
#     )
#     DocumentTestModel.replace_one(
#         {"_id": document.id}, new_doc, session=session
#     )
#     new_document = DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_str == "REPLACED_VALUE"
#
#
# def test_replace_with_session(document, session):
#     update_data = {"test_str": "REPLACED_VALUE"}
#     new_doc: DocumentTestModel = document.copy(update=update_data)
#     # document.test_str = "REPLACED_VALUE"
#     new_doc.replace(session=session)
#     new_document = DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_str == "REPLACED_VALUE"
#
#
# def test_update_one_with_session(document, session):
#     DocumentTestModel.update_one(
#         update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
#         filter_query={"_id": document.id, "test_list.test_str": "foo"},
#         session=session,
#     )
#     new_document = DocumentTestModel.get(document.id, session=session)
#     assert new_document.test_list[0].test_str == "foo_foo"
#
#
# def test_update_many_with_session(documents, session):
#     documents(10, "foo")
#     documents(7, "bar")
#     DocumentTestModel.update_many(
#         update_query={"$set": {"test_str": "bar"}},
#         filter_query={"test_str": "foo"},
#         session=session,
#     )
#     bar_documetns = DocumentTestModel.find_many(
#         {"test_str": "bar"}, session=session
#     ).to_list()
#     assert len(bar_documetns) == 17
#     foo_documetns = DocumentTestModel.find_many(
#         {"test_str": "foo"}, session=session
#     ).to_list()
#     assert len(foo_documetns) == 0
#
#
# def test_update_all_with_session(documents, session):
#     documents(10, "foo")
#     documents(7, "bar")
#     DocumentTestModel.update_all(
#         update_query={"$set": {"test_str": "smth_else"}}, session=session
#     )
#     bar_documetns = DocumentTestModel.find_many(
#         {"test_str": "bar"}, session=session
#     ).to_list()
#     assert len(bar_documetns) == 0
#     foo_documetns = DocumentTestModel.find_many(
#         {"test_str": "foo"}, session=session
#     ).to_list()
#     assert len(foo_documetns) == 0
#     smth_else_documetns = DocumentTestModel.find_many(
#         {"test_str": "smth_else"}, session=session
#     ).to_list()
#     assert len(smth_else_documetns) == 17
