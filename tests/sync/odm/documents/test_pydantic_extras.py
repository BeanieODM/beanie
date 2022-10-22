import pytest

from tests.sync.models import (
    DocumentWithExtras,
    DocumentWithPydanticConfig,
    DocumentWithExtrasKw,
)


def test_pydantic_extras():
    doc = DocumentWithExtras(num_1=2)
    doc.extra_value = "foo"
    doc.save()

    loaded_doc = DocumentWithExtras.get(doc.id).run()

    assert loaded_doc.extra_value == "foo"


@pytest.mark.skip(reason="setting extra to allow via class kwargs not working")
def test_pydantic_extras_kw():
    doc = DocumentWithExtrasKw(num_1=2)
    doc.extra_value = "foo"
    doc.save()

    loaded_doc = DocumentWithExtras.get(doc.id).run()

    assert loaded_doc.extra_value == "foo"


def test_fail_with_no_extras():
    doc = DocumentWithPydanticConfig(num_1=2)
    with pytest.raises(ValueError):
        doc.extra_value = "foo"
