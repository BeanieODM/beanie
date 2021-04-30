from typing import Union

from beanie.odm.fields import ExpressionField
from beanie.odm.operators.find import BaseFindOperator


class BaseFindBitwiseOperator(BaseFindOperator):
    """
    Base class for Bitwise find query operators
    """

    operator = ""

    def __init__(self, field: Union[str, ExpressionField], bitmask):
        """

        :param field: Union[str, ExpressionField]
        :param bitmask:
        """
        self.field = field
        self.bitmask = bitmask

    @property
    def query(self):
        return {self.field: {self.operator: self.bitmask}}


class BitsAllClear(BaseFindBitwiseOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAllClear/
    """

    operator = "$bitsAllClear"


class BitsAllSet(BaseFindBitwiseOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAllSet/
    """

    operator = "$bitsAllSet"


class BitsAnyClear(BaseFindBitwiseOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAnyClear/
    """

    operator = "$bitsAnyClear"


class BitsAnySet(BaseFindBitwiseOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/bitsAnySet/
    """

    operator = "$bitsAnySet"
