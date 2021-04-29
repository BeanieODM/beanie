from abc import abstractmethod

from beanie.odm.operators.update import BaseUpdateOperator


class BaseBitwiseUpdateOperator(BaseUpdateOperator):
    @property
    @abstractmethod
    def query(self):
        ...


class Bit(BaseBitwiseUpdateOperator):
    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$bit": self.expression}
