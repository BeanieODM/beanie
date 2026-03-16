from typing import Any, Generic, TypeVar

from beanie.odm.operators.find import BaseFindOperator

BitmaskType = TypeVar("BitmaskType", bound=Any)


class BaseFindBitwiseOperator(BaseFindOperator, Generic[BitmaskType]):
    operator = ""

    def __init__(self, field: Any, bitmask: BitmaskType):
        self.field = field
        self.bitmask = bitmask

    @property
    def query(self):
        return {self.field: {self.operator: self.bitmask}}


class BitsAllClear(BaseFindBitwiseOperator[BitmaskType]):
    """
    `$bitsAllClear` query operator

    MongoDB doc:
    <https://docs.mongodb.com/manual/reference/operator/query/bitsAllClear/>
    """

    operator = "$bitsAllClear"


class BitsAllSet(BaseFindBitwiseOperator[BitmaskType]):
    """
    `$bitsAllSet` query operator

    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAllSet/
    """

    operator = "$bitsAllSet"


class BitsAnyClear(BaseFindBitwiseOperator[BitmaskType]):
    """
    `$bitsAnyClear` query operator

    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAnyClear/
    """

    operator = "$bitsAnyClear"


class BitsAnySet(BaseFindBitwiseOperator[BitmaskType]):
    """
    `$bitsAnySet` query operator

    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAnySet/
    """

    operator = "$bitsAnySet"
