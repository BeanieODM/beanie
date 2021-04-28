from abc import abstractmethod

from beanie.odm.query_builder.operators.update import BaseUpdateOperator


class BaseArrayUpdateOperator(BaseUpdateOperator):
    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class AddToSet(BaseArrayUpdateOperator):
    operator = "$addToSet"


class Pop(BaseArrayUpdateOperator):
    operator = "$pop"


class Pull(BaseArrayUpdateOperator):
    operator = "$pull"


class Push(BaseArrayUpdateOperator):
    operator = "$push"


class PullAll(BaseArrayUpdateOperator):
    operator = "$pullAll"


class BaseArrayUpdateModifier(BaseUpdateOperator):
    @property
    @abstractmethod
    def query(self):
        ...


class Each(BaseArrayUpdateModifier):
    def __init__(self, lst: list):
        self.lst = lst

    @property
    def query(self):
        return {"$each": self.lst}


class Position(BaseArrayUpdateModifier):
    def __init__(self, num: int):
        self.num = num

    @property
    def query(self):
        return {"$position": self.num}


class Slice(BaseArrayUpdateModifier):
    def __init__(self, num: int):
        self.num = num

    @property
    def query(self):
        return {"$slice": self.num}


class Sort(BaseArrayUpdateModifier):
    def __init__(self, sort_specification: dict):
        self.sort_specification = sort_specification

    @property
    def query(self):
        return {"$sort": self.sort_specification}
