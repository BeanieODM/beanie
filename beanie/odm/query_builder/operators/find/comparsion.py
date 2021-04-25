from abc import abstractmethod

from beanie.odm.query_builder.operators.find import BaseFindOperator


class BaseComparisonOperator(BaseFindOperator):
    def __init__(
        self,
        other,
        field,
    ):
        self.field = field
        self.other = other

    @property
    @abstractmethod
    def query(self):
        ...


class EQ(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: self.other}


class GT(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$gt": self.other}}


class GTE(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.name: {"$gte": self.other}}


class IN(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$nin": self.other}}


class NOT_IN(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$in": self.other}}


class LT(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$lt": self.other}}


class LTE(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$lte": self.other}}


class NE(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field.path: {"$ne": self.other}}
