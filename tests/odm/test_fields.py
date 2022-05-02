import datetime
from pathlib import Path
from typing import Mapping, AbstractSet
import pytest
from pydantic import BaseModel, ValidationError

from beanie.odm.fields import PydanticObjectId
from beanie.odm.utils.dump import get_dict
from beanie.odm.utils.encoder import Encoder
from tests.odm.models import (
    DocumentWithCustomFiledsTypes,
    DocumentWithBsonEncodersFiledsTypes,
    DocumentTestModel,
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
        color="7fffd4", timestamp=datetime.datetime.utcnow()
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
        decimal=500.213,
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
    assert Encoder().encode(c1_fromdb) == Encoder().encode(c1)
    assert Encoder().encode(c2_fromdb) == Encoder().encode(c2)


async def test_hidden(document):
    document = await DocumentTestModel.find_one()

    assert "test_list" not in document.dict()


@pytest.mark.parametrize("exclude", [{"test_int"}, {"test_doc": {"test_int"}}])
async def test_param_exclude(document, exclude):
    document = await DocumentTestModel.find_one()

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
