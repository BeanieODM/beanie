from uuid import UUID

import pytest
from pydantic import BaseModel

from beanie import PydanticObjectId
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentWithCustomIdInt, DocumentWithCustomIdUUID


class A(BaseModel):
    id: PydanticObjectId


async def test_uuid_id():
    doc = DocumentWithCustomIdUUID(name="TEST")
    await doc.insert()
    new_doc = await DocumentWithCustomIdUUID.get(doc.id)
    assert isinstance(new_doc.id, UUID)


async def test_integer_id():
    doc = DocumentWithCustomIdInt(name="TEST", id=1)
    await doc.insert()
    new_doc = await DocumentWithCustomIdInt.get(doc.id)
    assert isinstance(new_doc.id, int)


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="supports only pydantic v2",
)
async def test_pydantic_object_id_validation_json():
    deserialized = A.model_validate_json('{"id": "5eb7cf5a86d9755df3a6c593"}')
    assert isinstance(deserialized.id, PydanticObjectId)
    assert str(deserialized.id) == "5eb7cf5a86d9755df3a6c593"
    assert deserialized.id == PydanticObjectId("5eb7cf5a86d9755df3a6c593")


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="supports only pydantic v2",
)
@pytest.mark.parametrize(
    "data",
    [
        "5eb7cf5a86d9755df3a6c593",
        PydanticObjectId("5eb7cf5a86d9755df3a6c593"),
    ],
)
async def test_pydantic_object_id_serialization(data):
    deserialized = A(**{"id": data})
    assert isinstance(deserialized.id, PydanticObjectId)
    assert str(deserialized.id) == "5eb7cf5a86d9755df3a6c593"
    assert deserialized.id == PydanticObjectId("5eb7cf5a86d9755df3a6c593")
