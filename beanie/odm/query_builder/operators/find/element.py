from abc import abstractmethod
from typing import List, Union

from beanie.odm.query_builder.operators.find import BaseFindOperator


class BaseFindElementOperator(BaseFindOperator):
    @property
    @abstractmethod
    def query(self):
        ...


class Exists(BaseFindElementOperator):
    def __init__(
        self,
        field,
        value: bool,
    ):
        self.field = field
        self.other = value

    @property
    def query(self):
        return {self.field: {"$exists": self.other}}


class Type(BaseFindElementOperator):
    def __init__(self, field, types: Union[List[str], str]):
        self.field = field
        self.types = types

    @property
    def query(self):
        return {self.field: {"$type": self.types}}
