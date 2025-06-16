import pytest

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentTestModelWithSerializationAlias


def data_maker():
    return DocumentTestModelWithSerializationAlias(test_int=1, test_str="test")


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="model serialization_alias is not supported in pydantic V1",
)
async def test_serialization_types_preserved_after_insertion():
    result = await DocumentTestModelWithSerializationAlias.insert_one(
        data_maker()
    )
    document = await DocumentTestModelWithSerializationAlias.get(result.id)
    assert document is not None
    assert document.test_int is not None
    assert document.test_str is not None
    dumped = document.model_dump()
    assert "test_int_serialize" in dumped
    assert "test_str_serialize" in dumped
    assert "test_int" not in dumped
    assert "test_str" not in dumped
