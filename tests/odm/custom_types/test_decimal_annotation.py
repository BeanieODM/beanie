from decimal import Decimal

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentWithDecimalField


def test_decimal_deserialize():
    m = DocumentWithDecimalField(amt=Decimal("1.4"))
    if IS_PYDANTIC_V2:
        m_json = m.model_dump_json()
        m_from_json = DocumentWithDecimalField.model_validate_json(m_json)
    else:
        m_json = m.json()
        m_from_json = DocumentWithDecimalField.parse_raw(m_json)
    assert isinstance(m_from_json.amt, Decimal)
    assert m_from_json.amt == Decimal("1.4")
