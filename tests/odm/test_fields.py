import pytest
from pydantic import BaseModel, ValidationError

from beanie.odm.fields import PydanticObjectId
from beanie.odm.utils.encoder import bsonable_encoder
from tests.odm.models import DocumentWithCustomFiledsTypes


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
        date="2000-12-24",
        time="12:24:12.000333",
        timedelta=4782453,
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
        date=1627498153,
        time="12:35",
        timedelta=4782453,
    )
    c1 = await custom1.insert()
    c2 = await custom2.insert()
    c1_fromdb = await DocumentWithCustomFiledsTypes.get(c1.id)
    c2_fromdb = await DocumentWithCustomFiledsTypes.get(c2.id)
    assert bsonable_encoder(c1_fromdb) == bsonable_encoder(c1)
    assert bsonable_encoder(c2_fromdb) == bsonable_encoder(c2)
