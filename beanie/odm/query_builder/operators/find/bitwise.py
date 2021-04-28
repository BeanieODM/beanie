from beanie.odm.query_builder.operators.find import BaseFindOperator


class BaseFindBitwiseOperator(BaseFindOperator):
    operator = ""

    def __init__(self, field, bitmask):
        self.field = field
        self.bitmask = bitmask

    @property
    def query(self):
        return {self.field: {self.operator: self.bitmask}}


class BitsAllClear(BaseFindBitwiseOperator):
    operator = "$bitsAllClear"


class BitsAllSet(BaseFindBitwiseOperator):
    operator = "$bitsAllSet"


class BitsAnyClear(BaseFindBitwiseOperator):
    operator = "$bitsAnyClear"


class BitsAnySet(BaseFindBitwiseOperator):
    operator = "$bitsAnySet"
