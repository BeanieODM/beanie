from abc import ABC
from typing import Any, Generic, TypeVar

from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateBitwiseOperator(BaseUpdateOperator, ABC): ...


_BitwiseOperatorExpressionType = TypeVar(
    "_BitwiseOperatorExpressionType", bound=dict[str, Any]
)


class Bit(BaseUpdateBitwiseOperator, Generic[_BitwiseOperatorExpressionType]):
    """
    `$bit` update query operator

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/bit/>
    """

    def __init__(self, expression: _BitwiseOperatorExpressionType):
        self.expression = expression

    @property
    def query(self):
        return {"$bit": self.expression}
