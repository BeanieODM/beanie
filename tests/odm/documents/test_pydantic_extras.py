import pytest

from tests.odm.models import (
    DocumentWithExtras,
    DocumentWithPydanticConfig,
    DocumentWithExtrasKw,
)


async def test_pydantic_extras():
    doc = DocumentWithExtras(num_1=2)
    doc.extra_value = "foo"
    await doc.save()

    loaded_doc = await DocumentWithExtras.get(doc.id)

    assert loaded_doc.extra_value == "foo"


@pytest.mark.skip(reason="setting extra to allow via class kwargs not working")
async def test_pydantic_extras_kw():
    doc = DocumentWithExtrasKw(num_1=2)
    doc.extra_value = "foo"
    await doc.save()

    loaded_doc = await DocumentWithExtras.get(doc.id)

    assert loaded_doc.extra_value == "foo"


async def test_fail_with_no_extras():
    doc = DocumentWithPydanticConfig(num_1=2)
    with pytest.raises(ValueError):
        doc.extra_value = "foo"
