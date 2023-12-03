from typing import Optional

import pytest
from bson import ObjectId
from pydantic import BaseModel, ValidationError

from beanie import PydanticObjectId
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    DocumentWithValidationOnSave,
    Lock,
    WindowWithValidationOnSave,
)


async def test_validate_on_insert():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        await doc.insert()


async def test_validate_on_replace():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    await doc.insert()
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        await doc.replace()


async def test_validate_on_save_changes():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    await doc.insert()
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        await doc.save_changes()


async def test_validate_on_save_keep_the_id_type():
    class UpdateModel(BaseModel):
        num_1: Optional[int] = None
        related: Optional[PydanticObjectId] = None

    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    await doc.insert()
    update = UpdateModel(related=PydanticObjectId())
    if IS_PYDANTIC_V2:
        doc = doc.model_copy(update=update.model_dump(exclude_unset=True))
    else:
        doc = doc.copy(update=update.dict(exclude_unset=True))
    doc.num_2 = 1000
    await doc.save()
    in_db = await DocumentWithValidationOnSave.get_motor_collection().find_one(
        {"_id": doc.id}
    )
    assert isinstance(in_db["related"], ObjectId)
    new_doc = await DocumentWithValidationOnSave.get(doc.id)
    assert isinstance(new_doc.related, PydanticObjectId)


async def test_validate_on_save_action():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    await doc.insert()
    assert doc.num_2 == 3


async def test_validate_on_save_skip_action():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    await doc.insert(skip_actions=["num_2_plus_1"])
    assert doc.num_2 == 2


async def test_validate_on_save_dbref():
    lock = Lock(k=1)
    await lock.insert()
    window = WindowWithValidationOnSave(
        x=1,
        y=1,
        lock=lock.to_ref(),  # this is what exactly we want to test
    )
    await window.insert()
