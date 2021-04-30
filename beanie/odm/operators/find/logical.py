from abc import ABC
from typing import Union

from beanie.odm.operators.find import BaseFindOperator


class BaseLogicalOperator(BaseFindOperator, ABC):
    ...


class LogicalOperatorForListOfExpressions(BaseLogicalOperator):  # TODO rename
    operator = ""

    def __init__(self, *expressions: Union[BaseFindOperator, dict, bool]):
        self.expressions = list(expressions)

    @property
    def query(self):
        if not self.expressions:
            raise AttributeError("At least one expression must be provided")
        if len(self.expressions) == 1:
            return self.expressions[0]
        return {self.operator: self.expressions}


class Or(LogicalOperatorForListOfExpressions):
    operator = "$or"


class And(LogicalOperatorForListOfExpressions):
    operator = "$and"


class Nor(BaseLogicalOperator):
    def __init__(self, *expressions: Union[BaseFindOperator, dict, bool]):
        self.expressions = list(expressions)

    @property
    def query(self):
        return {"$nor": self.expressions}


class Not(BaseLogicalOperator):
    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {"$not": self.expression}
