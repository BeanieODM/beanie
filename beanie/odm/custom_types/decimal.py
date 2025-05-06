from decimal import Decimal
from typing import Annotated

from bson import Decimal128
from pydantic import BeforeValidator

DecimalAnnotation = Annotated[
    Decimal,
    BeforeValidator(
        lambda v: v.to_decimal() if isinstance(v, Decimal128) else v
    ),
]

__all__ = ["DecimalAnnotation"]
