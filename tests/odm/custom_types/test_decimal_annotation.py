from decimal import Decimal

from tests.odm.models import DocumentWithDecimalField


def test_decimal_deserialize():
    m = DocumentWithDecimalField(amt=Decimal("1.4"))
    m_json = m.model_dump_json()
    m_from_json = DocumentWithDecimalField.model_validate_json(m_json)

    assert isinstance(m_from_json.amt, Decimal)
    assert m_from_json.amt == Decimal("1.4")
