import pytest

from tests.odm_sync.models import (
    SyncDocumentWithExtras,
    SyncDocumentWithPydanticConfig,
    SyncDocumentWithExtrasKw,
)


def test_pydantic_extras():
    doc = SyncDocumentWithExtras(num_1=2)
    doc.extra_value = "foo"
    doc.save()

    loaded_doc = SyncDocumentWithExtras.get(doc.id)

    assert loaded_doc.extra_value == "foo"


@pytest.mark.skip(reason="setting extra to allow via class kwargs not working")
def test_pydantic_extras_kw():
    doc = SyncDocumentWithExtrasKw(num_1=2)
    doc.extra_value = "foo"
    doc.save()

    loaded_doc = SyncDocumentWithExtras.get(doc.id)

    assert loaded_doc.extra_value == "foo"


def test_fail_with_no_extras():
    doc = SyncDocumentWithPydanticConfig(num_1=2)
    with pytest.raises(ValueError):
        doc.extra_value = "foo"
