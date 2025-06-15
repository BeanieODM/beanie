import decimal
from typing import Annotated

import bson
import pydantic

DecimalAnnotation = Annotated[
    decimal.Decimal,
    pydantic.BeforeValidator(lambda v: v.to_decimal() if isinstance(v, bson.Decimal128) else v),
]
