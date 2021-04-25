from abc import abstractmethod
from typing import Union

from beanie.odm.query_builder.operators.find import BaseFindOperator


class BaseLogicalOperator(BaseFindOperator):
    @property
    @abstractmethod
    def query(self):
        ...


def get_expression_dict(expression: Union[BaseFindOperator, dict]):
    if isinstance(expression, BaseFindOperator):
        return expression.query
    elif isinstance(expression, dict):
        return expression
    else:
        raise Exception  # TODO come up with exception


class LogicalOperatorForList(BaseLogicalOperator):  # TODO rename
    operator = ""

    def __init__(self, *expressions: Union[BaseFindOperator, dict]):
        self.expressions = [
            get_expression_dict(expression) for expression in expressions
        ]

    @property
    def query(self):
        if not self.expressions:
            raise Exception  # TODO come up with exception
        if len(self.expressions) == 1:
            return self.expressions[0]
        return {self.operator: self.expressions}


class OR(LogicalOperatorForList):
    operator = "$or"


class AND(LogicalOperatorForList):
    operator = "$and"


class NOR(LogicalOperatorForList):
    operator = "$nor"


class NOT(BaseLogicalOperator):
    def __init__(self, expression):
        self.expression = get_expression_dict(expression)

    @property
    def query(self):
        return {"$not": self.expression}
