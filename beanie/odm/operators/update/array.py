from typing import Any, Generic, TypeVar

from beanie.odm.operators.update import BaseUpdateOperator

_ArrayExpressionType = TypeVar("_ArrayExpressionType", bound=dict[str, Any])


class BaseUpdateArrayOperator(
    BaseUpdateOperator, Generic[_ArrayExpressionType]
):
    operator = ""

    def __init__(self, expression: _ArrayExpressionType):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class AddToSet(BaseUpdateArrayOperator[_ArrayExpressionType]):
    """
    `$addToSet` update array query operator

    Example:

    ```python
    class Sample(Document):
        results: List[int]

    AddToSet({Sample.results: 2})
    ```

    Will return query object like

    ```python
    {"$addToSet": {"results": 2}}
    ```

    MongoDB docs:
    <https://docs.mongodb.com/manual/reference/operator/update/addToSet/>
    """

    operator = "$addToSet"


class Pop(BaseUpdateArrayOperator[_ArrayExpressionType]):
    """
    `$pop` update array query operator

    Example:

    ```python
    class Sample(Document):
        results: List[int]

    Pop({Sample.results: 2})
    ```

    Will return query object like

    ```python
    {"$pop": {"results": -1}}
    ```

    MongoDB docs:
    <https://docs.mongodb.com/manual/reference/operator/update/pop/>
    """

    operator = "$pop"


class Pull(BaseUpdateArrayOperator[_ArrayExpressionType]):
    """
    `$pull` update array query operator

    Example:

    ```python
    class Sample(Document):
        results: List[int]

    Pull(In(Sample.result: [1,2,3,4,5])
    ```

    Will return query object like

    ```python
    {"$pull": { "results": { $in: [1,2,3,4,5] }}}
    ```

    MongoDB docs:
    <https://docs.mongodb.com/manual/reference/operator/update/pull/>
    """

    operator = "$pull"


class Push(BaseUpdateArrayOperator[_ArrayExpressionType]):
    """
    `$push` update array query operator

    Example:

    ```python
    class Sample(Document):
        results: List[int]

    Push({Sample.results: 1})
    ```

    Will return query object like

    ```python
    {"$push": { "results": 1}}
    ```

    MongoDB docs:
    <https://docs.mongodb.com/manual/reference/operator/update/push/>
    """

    operator = "$push"


class PullAll(BaseUpdateArrayOperator[_ArrayExpressionType]):
    """
    `$pullAll` update array query operator

    Example:

    ```python
    class Sample(Document):
        results: List[int]

    PullAll({ Sample.results: [ 0, 5 ] })
    ```

    Will return query object like

    ```python
    {"$pullAll": { "results": [ 0, 5 ] }}
    ```

    MongoDB docs:
    <https://docs.mongodb.com/manual/reference/operator/update/pullAll/>
    """

    operator = "$pullAll"
