from uuid import uuid4

import pytest

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
    json_schema = doc.model_json_schema()

    assert json_schema["properties"]["amt"]["anyOf"][0]["type"] == "number"
    assert json_schema["properties"]["amt"]["anyOf"][1]["type"] == "string"
    assert (
        json_schema["properties"]["other_amt"]["anyOf"][0]["type"] == "number"
    )
    assert (
        json_schema["properties"]["other_amt"]["anyOf"][1]["type"] == "string"
    )


def test_schema_export_of_model_with_pydanticobjectid():
    doc = DocumentWithIndexedObjectId(
        pyid="5f8d0a8b0b7e3a1e4c9f4b1e", uuid=uuid4(), email="test@test.com"
    )
    json_schema = doc.model_json_schema()

    assert (
        json_schema["properties"]["_id"]["anyOf"][0]["$ref"]
        == "#/$defs/PydanticObjectId"
    )
    assert (
        json_schema["properties"]["pyid"]["$ref"] == "#/$defs/PydanticObjectId"
    )


def test_schema_export_of_model_with_link():
    json_schema = DocumentWithLink.model_json_schema()

    link_alternate_representation = json_schema["properties"]["link"]["anyOf"]

    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"


def test_schema_export_of_model_with_optional_link():
    json_schema = DocumentWithOptionalLink.model_json_schema()
    link_alternate_representation = json_schema["properties"]["link"]["anyOf"]
    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"
    assert link_alternate_representation[2]["type"] == "null"


def test_schema_export_of_model_with_list_link():
    json_schema = DocumentWithListLink.model_json_schema()
    link_alternate_representation = json_schema["properties"]["link"]["items"][
        "anyOf"
    ]
    link_definition = json_schema["properties"]["link"]["type"]

    assert link_definition == "array"
    assert link_alternate_representation[0]["type"] == "object"
    assert link_alternate_representation[1]["type"] == "object"


def test_schema_export_of_model_with_backlink():
    json_schema = DocumentWithBackLink.model_json_schema()

    back_link_definition = json_schema["properties"]["back_link"]["type"]

    assert back_link_definition == "object"


def test_schema_export_of_model_with_list_backlink():
    json_schema = DocumentWithListBackLink.model_json_schema()

    assert json_schema["properties"]["back_link"]["type"] == "array"
    assert json_schema["properties"]["back_link"]["items"]["type"] == "object"


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
