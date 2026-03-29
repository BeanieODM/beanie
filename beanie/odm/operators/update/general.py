from typing import Any, Generic, TypeVar

from beanie.odm.operators.update import BaseUpdateOperator

_UpdateExpressionType = TypeVar("_UpdateExpressionType", bound=dict[str, Any])


class BaseUpdateGeneralOperator(
    BaseUpdateOperator, Generic[_UpdateExpressionType]
):
    operator = ""

    def __init__(self, expression: _UpdateExpressionType):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class Set(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$set` update query operator

    Example:

    ```python
    class Sample(Document):
        one: int

    Set({Sample.one: 2})
    ```

    Will return query object like

    ```python
    {"$set": {"one": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/set/>
    """

    operator = "$set"


class SetRevisionId:
    """
    `$set` update query operator, with `revision_id` field as expression

    Example:

    ```python
    class Sample(Document):
        one: int

    SetRevisionId(2)
    ```

    Will return query object like

    ```python
    {"$set": {"revision_id": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/set/>
    """

    def __init__(self, revision_id: Any):
        self.revision_id = revision_id
        self.operator = "$set"
        self.expression = {"revision_id": self.revision_id}

    @property
    def query(self):
        return {self.operator: self.expression}


class CurrentDate(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$currentDate` update query operator

    Example:

    ```python
    class Sample(Document):
        ts: datetime

    CurrentDate({Sample.ts: True})
    ```

    Will return query object like

    ```python
    {"$currentDate": {"ts": True}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/currentDate/>
    """

    operator = "$currentDate"


class Inc(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$inc` update query operator

    Example:

    ```python
    class Sample(Document):
        one: int

    Inc({Sample.one: 2})
    ```

    Will return query object like

    ```python
    {"$inc": {"one": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/inc/>
    """

    operator = "$inc"


class Min(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$min` update query operator

    Example:

    ```python
    class Sample(Document):
        one: int

    Min({Sample.one: 2})
    ```

    Will return query object like

    ```python
    {"$min": {"one": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/min/>
    """

    operator = "$min"


class Max(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$max` update query operator

    Example:

    ```python
    class Sample(Document):
        one: int

    Max({Sample.one: 2})
    ```

    Will return query object like

    ```python
    {"$max": {"one": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/max/>
    """

    operator = "$max"


class Mul(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$mul` update query operator

    Example:

    ```python
    class Sample(Document):
        one: int

    Mul({Sample.one: 2})
    ```

    Will return query object like

    ```python
    {"$mul": {"one": 2}}
    ```

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/mul/>
    """

    operator = "$mul"


class Rename(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$rename` update query operator

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/rename/>
    """

    operator = "$rename"


class SetOnInsert(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$setOnInsert` update query operator

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/setOnInsert/>
    """

    operator = "$setOnInsert"


class Unset(BaseUpdateGeneralOperator[_UpdateExpressionType]):
    """
    `$unset` update query operator

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/update/unset/>
    """

    operator = "$unset"
