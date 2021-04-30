from abc import ABC
from typing import Union

from beanie.odm.operators.find import BaseFindOperator


class BaseFindLogicalOperator(BaseFindOperator, ABC):
    ...


class LogicalOperatorForListOfExpressions(BaseFindLogicalOperator):
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


class Nor(BaseFindLogicalOperator):
    def __init__(self, *expressions: Union[BaseFindOperator, dict, bool]):
        self.expressions = list(expressions)

    @property
    def query(self):
        return {"$nor": self.expressions}


class Not(BaseFindLogicalOperator):
    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {"$not": self.expression}
