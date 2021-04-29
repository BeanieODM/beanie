from abc import ABC

from beanie.odm.operators.update import BaseUpdateOperator


class BaseBitwiseUpdateOperator(BaseUpdateOperator, ABC):
    ...


class Bit(BaseBitwiseUpdateOperator):
    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$bit": self.expression}
