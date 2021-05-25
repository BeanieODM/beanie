from abc import ABC
from typing import Any, Dict, Mapping, Union

from beanie.odm.operators.find import BaseFindOperator


class BaseFindLogicalOperator(BaseFindOperator, ABC):
    ...


class LogicalOperatorForListOfExpressions(BaseFindLogicalOperator):
    operator: str = ""

    def __init__(
        self,
        *expressions: Union[
            BaseFindOperator, Dict[str, Any], Mapping[str, Any]
        ]
    ):
        self.expressions = list(expressions)

    @property
    def query(self) -> Union[Dict[str, Any], Mapping[str, Any]]:
        if not self.expressions:
            raise AttributeError("At least one expression must be provided")
        if len(self.expressions) == 1:
            return self.expressions[0]
        return {self.operator: self.expressions}


class Or(LogicalOperatorForListOfExpressions):
    """
    `$or` query operator

    Example:

    ```python
    class Product(Document):
        price: float
        category: str

    Or({Product.price<10}, {Product.category=="Sweets"})
    ```

    Will return query object like

    ```python
    {"$or": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/query/or/>
    """

    operator = "$or"


class And(LogicalOperatorForListOfExpressions):
    """
    `$and` query operator

    Example:

    ```python
    class Product(Document):
        price: float
        category: str

    And({Product.price<10}, {Product.category=="Sweets"})
    ```

    Will return query object like

    ```python
    {"$and": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/query/and/>
    """

    operator = "$and"


class Nor(BaseFindLogicalOperator):
    """
    `$nor` query operator

    Example:

    ```python
    class Product(Document):
        price: float
        category: str

    Nor({Product.price<10}, {Product.category=="Sweets"})
    ```

    Will return query object like

    ```python
    {"$nor": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/query/nor/>
    """

    def __init__(
        self,
        *expressions: Union[
            BaseFindOperator, Dict[str, Any], Mapping[str, Any], bool
        ]
    ):
        self.expressions = list(expressions)

    @property
    def query(self):
        return {"$nor": self.expressions}


class Not(BaseFindLogicalOperator):
    """
    `$not` query operator

    Example:

    ```python
    class Product(Document):
        price: float
        category: str

    Not({Product.price<10})
    ```

    Will return query object like

    ```python
    {"$not": {"price": {"$lt": 10}}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/query/not/>
    """

    def __init__(self, expression: Union[Dict[str, Any], Mapping[str, Any]]):
        self.expression = expression

    @property
    def query(self):
        return {"$not": self.expression}
