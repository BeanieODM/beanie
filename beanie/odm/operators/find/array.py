from abc import ABC

from beanie.odm.operators.find import BaseFindOperator


class BaseFindArrayOperator(BaseFindOperator, ABC):
    ...


class All(BaseFindArrayOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/all
    """

    def __init__(
        self,
        field,
        values: list,
    ):
        self.field = field
        self.values = values

    @property
    def query(self):
        return {self.field: {"$all": self.values}}


class ElemMatch(BaseFindArrayOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/elemMatch/
    """

    def __init__(
        self,
        field,
        expression: dict,
    ):
        self.field = field
        self.expression = expression

    @property
    def query(self):
        return {self.field: {"$elemMatch": self.expression}}


class Size(BaseFindArrayOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/size/
    """

    def __init__(
        self,
        field,
        num: int,
    ):
        self.field = field
        self.num = num

    @property
    def query(self):
        return {self.field: {"$size": self.num}}
