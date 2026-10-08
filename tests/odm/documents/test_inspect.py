from uuid import UUID

import pytest
from bson import ObjectId
from pydantic import create_model

from beanie import Document, PydanticObjectId, init_beanie
from beanie.odm.models import InspectionError, InspectionStatuses
from tests.odm.models import DocumentTestModel, DocumentTestModelFailInspection


async def test_inspect_ok(documents):
    await documents(10, "smth")
    result = await DocumentTestModel.inspect_collection()
    assert result.status == InspectionStatuses.OK
    assert result.errors == []


async def test_inspect_fail(documents):
    await documents(10, "smth")
    result = await DocumentTestModelFailInspection.inspect_collection()
    assert result.status == InspectionStatuses.FAIL
    assert len(result.errors) == 10
    assert (
        "1 validation error for DocumentTestModelFailInspection"
        in result.errors[0].error
    )


async def test_inspect_ok_with_session(documents, session):
    await documents(10, "smth")
    result = await DocumentTestModel.inspect_collection(session=session)
    assert result.status == InspectionStatuses.OK
    assert result.errors == []


@pytest.mark.parametrize(
    "document_id",
    [
        PydanticObjectId(),
        UUID("12345678-1234-1234-9234-123456789abc"),
        UUID("12345678-1234-4234-9234-123456789abc"),
        "custom-id",
        42,
        {"tenant": "test", "number": 42},
    ],
)
async def test_inspect_preserves_custom_ids(db, document_id):
    CustomIdDocument = create_model(
        "CustomIdDocument",
        __base__=Document,
        id=(type(document_id), ...),
        name=(str, ...),
    )

    await init_beanie(database=db, document_models=[CustomIdDocument])
    collection = CustomIdDocument.get_pymongo_collection()
    try:
        document = CustomIdDocument(id=document_id, name="valid")
        await document.insert()
        assert (await CustomIdDocument.inspect_collection()).errors == []

        await collection.update_one({}, {"$set": {"name": ["invalid"]}})
        stored_id = (await collection.find_one({}))["_id"]
        result = await CustomIdDocument.inspect_collection()

        assert result.status == InspectionStatuses.FAIL
        assert len(result.errors) == 1
        assert result.errors[0].document_id == stored_id
        assert type(result.errors[0].document_id) is type(stored_id)
        assert "name" in result.errors[0].error
    finally:
        await collection.drop()


def test_inspection_error_serializes_object_id():
    document_id = ObjectId()
    error = InspectionError(document_id=document_id, error="invalid")
    assert error.model_dump(mode="json") == {
        "document_id": str(document_id),
        "error": "invalid",
    }
