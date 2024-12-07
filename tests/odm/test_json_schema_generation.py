from uuid import uuid4

import pytest

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    DocumentWithBackLink,
    DocumentWithDecimalField,
    DocumentWithIndexedObjectId,
    DocumentWithLink,
    DocumentWithListBackLink,
    DocumentWithListLink,
    DocumentWithOptionalLink,
)


def test_schema_export_of_model_with_decimal_field():
    doc = DocumentWithDecimalField(amt=0.1, other_amt=3.5)
    if IS_PYDANTIC_V2:
        json_schema = doc.model_json_schema()

        assert json_schema["properties"]["amt"]["anyOf"][0]["type"] == "number"
        assert json_schema["properties"]["amt"]["anyOf"][1]["type"] == "string"
        assert (
            json_schema["properties"]["other_amt"]["anyOf"][0]["type"]
            == "number"
        )
        assert (
            json_schema["properties"]["other_amt"]["anyOf"][1]["type"]
            == "string"
        )

    else:
        json_schema = doc.schema()

        assert json_schema["properties"]["amt"]["type"] == "number"
        assert json_schema["properties"]["other_amt"]["type"] == "number"


def test_schema_export_of_model_with_pydanticobjectid():
    doc = DocumentWithIndexedObjectId(
        pyid="5f8d0a8b0b7e3a1e4c9f4b1e", uuid=uuid4(), email="test@test.com"
    )
    if IS_PYDANTIC_V2:
        json_schema = doc.model_json_schema()

        assert json_schema["properties"]["_id"]["anyOf"][0]["type"] == "string"
        assert json_schema["properties"]["pyid"]["type"] == "string"
    else:
        json_schema = doc.schema()

        assert json_schema["properties"]["_id"]["type"] == "string"
        assert json_schema["properties"]["pyid"]["type"] == "string"


def test_schema_export_of_model_with_link():
    if IS_PYDANTIC_V2:
        json_schema = DocumentWithLink.model_json_schema()

        link_alternate_representation = json_schema["properties"]["link"][
            "anyOf"
        ]
    else:
        json_schema = DocumentWithLink.schema()

        link_alternate_representation = json_schema["definitions"][
            "DocumentWithLink"
        ]["properties"]["link"]["anyOf"]

    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="schema dumping support is more complete with pydantic v2",
)
def test_schema_export_of_model_with_optional_link():
    if IS_PYDANTIC_V2:
        json_schema = DocumentWithOptionalLink.model_json_schema()
    else:
        json_schema = DocumentWithOptionalLink.schema()

    link_alternate_representation = json_schema["properties"]["link"]["anyOf"]
    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"
    assert link_alternate_representation[2]["type"] == "null"


def test_schema_export_of_model_with_list_link():
    if IS_PYDANTIC_V2:
        json_schema = DocumentWithListLink.model_json_schema()

        link_alternate_representation = json_schema["properties"]["link"][
            "items"
        ]["anyOf"]
        link_definition = json_schema["properties"]["link"]["type"]
    else:
        json_schema = DocumentWithListLink.schema()

        link_alternate_representation = json_schema["definitions"][
            "DocumentWithListLink"
        ]["properties"]["link"]["items"]["anyOf"]
        link_definition = json_schema["definitions"]["DocumentWithListLink"][
            "properties"
        ]["link"]["type"]

    assert link_definition == "array"
    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"


def test_schema_export_of_model_with_backlink():
    if IS_PYDANTIC_V2:
        json_schema = DocumentWithBackLink.model_json_schema()

        back_link_definition = json_schema["properties"]["back_link"]["type"]
    else:
        json_schema = DocumentWithBackLink.schema()

        back_link_definition = json_schema["definitions"][
            "DocumentWithBackLink"
        ]["properties"]["back_link"]["anyOf"][1]["type"]

    assert back_link_definition == "object"


def test_schema_export_of_model_with_list_backlink():
    if IS_PYDANTIC_V2:
        json_schema = DocumentWithListBackLink.model_json_schema()

        assert json_schema["properties"]["back_link"]["type"] == "array"
        assert (
            json_schema["properties"]["back_link"]["items"]["type"] == "object"
        )
    else:
        json_schema = DocumentWithListBackLink.schema()

        assert (
            json_schema["definitions"]["DocumentWithListBackLink"][
                "properties"
            ]["back_link"]["type"]
            == "array"
        )
        assert (
            json_schema["definitions"]["DocumentWithListBackLink"][
                "properties"
            ]["back_link"]["items"]["anyOf"][1]["type"]
            == "object"
        )


@pytest.mark.skipif(
    not IS_PYDANTIC_V2,
    reason="schema dumping support is more complete with pydantic v2",
)
@pytest.mark.parametrize(
    "model_type",
    [
        DocumentWithDecimalField,
        DocumentWithIndexedObjectId,
        DocumentWithLink,
        DocumentWithOptionalLink,
        DocumentWithListLink,
        DocumentWithBackLink,
        DocumentWithListBackLink,
    ],
)
def test_json_serialization_of_model(model_type):
    validation_schema = model_type.model_json_schema(mode="serialization")
    assert validation_schema is not None
    assert isinstance(validation_schema, dict)
