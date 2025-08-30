import datetime
from decimal import Decimal
from pathlib import Path
from typing import AbstractSet, Mapping
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from beanie import Document
from beanie.exceptions import CollectionWasNotInitialized
from beanie.odm.fields import PydanticObjectId
from beanie.odm.utils.dump import get_dict
from beanie.odm.utils.encoder import Encoder
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    DocumentTestModel,
    DocumentTestModelIndexFlagsAnnotated,
    DocumentWithBsonEncodersFiledsTypes,
    DocumentWithComputedField,
    DocumentWithCustomFiledsTypes,
    DocumentWithDeprecatedHiddenField,
    DocumentWithExcludedField,
    Sample,
)


class M(BaseModel):
    p: PydanticObjectId


def test_pydantic_object_id_wrong_input():
    with pytest.raises(ValidationError):
        M(p="test")


def test_pydantic_object_id_bytes_input():
    p = PydanticObjectId()
    m = M(p=str(p).encode("utf-8"))
    assert m.p == p
    with pytest.raises(ValidationError):
        M(p=b"test")


async def test_bson_encoders_filed_types():
    custom = DocumentWithBsonEncodersFiledsTypes(
        color="7fffd4",
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    encoded = get_dict(custom)
    assert isinstance(encoded["timestamp"], str)
    c = await custom.insert()
    c_fromdb = await DocumentWithBsonEncodersFiledsTypes.get(c.id)
    assert c_fromdb.color.as_hex() == c.color.as_hex()
    assert isinstance(c_fromdb.timestamp, datetime.datetime)
    assert c_fromdb.timestamp, custom.timestamp


async def test_custom_filed_types():
    custom1 = DocumentWithCustomFiledsTypes(
        color="#753c38",
        decimal=500,
        secret_bytes=b"secret_bytes",
        secret_string="super_secret_password",
        ipv4address="127.0.0.1",
        ipv4interface="192.0.2.5/24",
        ipv4network="192.0.2.0/24",
        ipv6address="::abc:7:def",
        ipv6interface="2001:db00::2/24",
        ipv6network="2001:db00::0/24",
        timedelta=4782453,
        set_type={"one", "two", "three"},
        tuple_type=tuple([3, "string"]),
        path="/etc/hosts",
    )
    custom2 = DocumentWithCustomFiledsTypes(
        color="magenta",
        decimal=Decimal("3.14") + Decimal(10) ** Decimal(-18),
        secret_bytes=b"secret_bytes",
        secret_string="super_secret_password",
        ipv4address="127.0.0.1",
        ipv4interface="192.0.2.5/24",
        ipv4network="192.0.2.0/24",
        ipv6address="::abc:7:def",
        ipv6interface="2001:db00::2/24",
        ipv6network="2001:db00::0/24",
        timedelta=4782453,
        set_type=["one", "two", "three"],
        tuple_type=[3, "three"],
        path=Path("C:\\Windows"),
    )
    c1 = await custom1.insert()
    c2 = await custom2.insert()
    c1_fromdb = await DocumentWithCustomFiledsTypes.get(c1.id)
    c2_fromdb = await DocumentWithCustomFiledsTypes.get(c2.id)
    assert set(c1_fromdb.set_type) == set(c1.set_type)
    assert set(c2_fromdb.set_type) == set(c2.set_type)
    c1_fromdb.set_type = c2_fromdb.set_type = c1.set_type = c2.set_type = None
    c1_fromdb.revision_id = None
    c2_fromdb.revision_id = None
    c1_encoded = Encoder().encode(c1)
    c1_fromdb_encoded = Encoder().encode(c1_fromdb)
    c2_encoded = Encoder().encode(c2)
    c2_fromdb_encoded = Encoder().encode(c2_fromdb)
    assert c1_fromdb_encoded == c1_encoded
    assert c2_fromdb_encoded == c2_encoded
    assert Decimal(str(custom1.decimal)) == Decimal(
        str(c1_encoded.get("decimal"))
    )
    assert Decimal(str(custom2.decimal)) == Decimal(
        str(c2_encoded.get("decimal"))
    )


async def test_excluded(document):
    doc = DocumentWithExcludedField(included_field=1, excluded_field=2)
    await doc.insert()
    stored_doc = await DocumentWithExcludedField.get(doc.id)
    assert stored_doc is not None
    if IS_PYDANTIC_V2:
        assert "included_field" in stored_doc.model_dump()
        assert "excluded_field" not in stored_doc.model_dump()
    else:
        assert "included_field" in stored_doc.dict()
        assert "excluded_field" not in stored_doc.dict()


@pytest.mark.skipif(not IS_PYDANTIC_V2, reason="Test only for Pydantic v2")
async def test_computed_field():
    doc = DocumentWithComputedField(num=1)
    assert doc.doubled == 2

    await doc.insert()
    stored_doc = await DocumentWithComputedField.get(doc.id)
    assert stored_doc and stored_doc.doubled == 2

    stored_doc.num = 2
    assert stored_doc.doubled == 4

    await stored_doc.replace()
    replaced_doc = await DocumentWithComputedField.get(doc.id)
    assert replaced_doc and replaced_doc.doubled == 4


@pytest.mark.skipif(not IS_PYDANTIC_V2, reason="Test only for Pydantic v2")
async def test_computed_field_setter():
    doc = DocumentWithComputedField(num=1)
    await doc.insert()
    cached_uui = doc.cacheable_uuid
    db_raw_data = (
        await DocumentWithComputedField.get_pymongo_collection().find_one(
            {"_id": doc.id}
        )
    )
    assert db_raw_data == {
        "_id": doc.id,
        "num": 1,
        "doubled": 2,
        "cacheable_uuid": cached_uui,
    }

    fetched_doc = await DocumentWithComputedField.get(doc.id)
    assert fetched_doc and fetched_doc.cacheable_uuid != cached_uui


async def test_hidden(deprecated_init_beanie):
    document = DocumentWithDeprecatedHiddenField(test_hidden=["abc", "def"])
    await document.insert()
    document = await DocumentWithDeprecatedHiddenField.find_one()
    if IS_PYDANTIC_V2:
        assert "test_hidden" not in document.model_dump()
    else:
        assert "test_hidden" not in document.dict()


def test_revision_id_not_in_schema():
    """Check if there is a `revision_id` slipping into the schema."""

    class Foo(Document):
        """Dummy document."""

        bar: int = 3

    if IS_PYDANTIC_V2:
        schema = Foo.model_json_schema()
    else:
        schema = Foo.schema()
    assert "revision_id" not in schema["properties"]

    # check that the document has not been initialized,
    # as otherwise the `revision_id` is normally gone from the schema.
    with pytest.raises(CollectionWasNotInitialized):
        Foo.get_settings()


@pytest.mark.parametrize("exclude", [{"test_int"}, {"test_doc": {"test_int"}}])
async def test_param_exclude(document, exclude):
    document = await DocumentTestModel.find_one()
    if IS_PYDANTIC_V2:
        doc_dict = document.model_dump(exclude=exclude)
    else:
        doc_dict = document.dict(exclude=exclude)
    if isinstance(exclude, AbstractSet):
        for k in exclude:
            assert k not in doc_dict
    elif isinstance(exclude, Mapping):
        for k, v in exclude.items():
            if isinstance(v, bool) and v:
                assert k not in doc_dict
            elif isinstance(v, AbstractSet):
                for another_k in v:
                    assert another_k not in doc_dict[k]


def test_expression_fields():
    assert Sample.nested.integer == "nested.integer"
    assert Sample.nested["integer"] == "nested.integer"


def test_indexed_field() -> None:
    """Test that fields can be declared and instantiated with Indexed()
    and Annotated[..., Indexed()]."""

    # No error should be raised the document is properly initialized
    # and `Indexed` is implemented correctly.
    DocumentTestModelIndexFlagsAnnotated(
        str_index="test",
        str_index_annotated="test",
        uuid_index=uuid4(),
        uuid_index_annotated=uuid4(),
    )
