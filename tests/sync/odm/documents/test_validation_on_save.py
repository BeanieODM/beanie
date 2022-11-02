import pytest
from pydantic import ValidationError

from tests.sync.models import DocumentWithValidationOnSave


def test_validate_on_insert():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        doc.insert()


def test_validate_on_replace():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.insert()
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        doc.replace()


def test_validate_on_save_changes():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.insert()
    doc.num_1 = "wrong_value"
    with pytest.raises(ValidationError):
        doc.save_changes()


def test_validate_on_save_action():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.insert()
    assert doc.num_2 == 3


def test_validate_on_save_skip_action():
    doc = DocumentWithValidationOnSave(num_1=1, num_2=2)
    doc.insert(skip_actions=["num_2_plus_1"])
    assert doc.num_2 == 2
