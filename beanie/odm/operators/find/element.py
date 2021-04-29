from abc import ABC
from typing import List, Union

from beanie.odm.operators.find import BaseFindOperator


class BaseFindElementOperator(BaseFindOperator, ABC):
    ...


class Exists(BaseFindElementOperator):
    def __init__(
        self,
        field,
        value: bool,
    ):
        self.field = field
        self.value = value

    @property
    def query(self):
        return {self.field: {"$exists": self.value}}


class Type(BaseFindElementOperator):
    def __init__(self, field, types: Union[List[str], str]):
        self.field = field
        self.types = types

    @property
    def query(self):
        return {self.field: {"$type": self.types}}
