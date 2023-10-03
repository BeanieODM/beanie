import pytest
from pydantic import ValidationError

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
