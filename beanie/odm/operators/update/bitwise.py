from abc import ABC

from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateBitwiseOperator(BaseUpdateOperator, ABC):
    ...


class Bit(BaseUpdateBitwiseOperator):
    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$bit": self.expression}
