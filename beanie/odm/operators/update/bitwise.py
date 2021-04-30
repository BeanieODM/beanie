from abc import ABC

from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateBitwiseOperator(BaseUpdateOperator, ABC):
    """
    Base class for bitwise update operator
    """

    ...


class Bit(BaseUpdateBitwiseOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/bit/
    """

    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$bit": self.expression}
