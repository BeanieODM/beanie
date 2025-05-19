import pytest
from pydantic import BaseModel, Field

from beanie import BackLink, Link, PydanticObjectId
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    DocumentTestModelWithSoftDelete,
    DocumentWithBackLink,
    DocumentWithLink,
)


class TestModel(BaseModel):
    my_id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    fake_doc: Link[DocumentTestModelWithSoftDelete]


def data_maker():
    return TestModel(
        my_id="5f4e3f3b7c0c9d001f7d4c8e",
        fake_doc=DocumentTestModelWithSoftDelete(
            test_int=1, test_str="test", id="5f4e3f3b7c0c9d001f7d4c8f"
        ),
    )


def data_maker_backlink_pair():
    back_link_doc = DocumentWithBackLink(
        id="5f4e3f3b7c0c9d001f7d4c8e",
        back_link=BackLink(document_class=DocumentWithLink),
    )
    link_doc = DocumentWithLink(
        id="5f4e3f3b7c0c9d001f7d4c8f", link=back_link_doc
    )
    return link_doc, back_link_doc


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="model dumping support is more complete with pydantic v2",
)
def test_id_types_preserved_when_dumping_to_python():
    dumped = data_maker().model_dump(mode="python")
    assert isinstance(dumped["my_id"], PydanticObjectId)
    assert isinstance(dumped["fake_doc"]["id"], PydanticObjectId)


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="model dumping support is more complete with pydantic v2",
)
def test_id_types_serialized_when_dumping_to_json():
    dumped = data_maker().model_dump(mode="json")
    assert isinstance(dumped["my_id"], str)
    assert isinstance(dumped["fake_doc"]["id"], str)


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="model dumping support is more complete with pydantic v2",
)
def test_backlink_serialization_to_json_when_fetched():
    link_doc, back_link_doc = data_maker_backlink_pair()

    # presume we have fetched this BackLink by using fetch_links=True, nesting_depth=1
    back_link_doc.back_link = link_doc

    dumped_model = back_link_doc.model_dump(mode="json")

    assert dumped_model["back_link"] == {"collection": "DocumentWithLink"}
