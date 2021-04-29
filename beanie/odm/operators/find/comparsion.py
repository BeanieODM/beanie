from beanie.odm.operators.find import BaseFindOperator


class BaseComparisonOperator(BaseFindOperator):
    operator = ""

    def __init__(
        self,
        field,
        other,
    ):
        self.field = field
        self.other = other

    @property
    def query(self):
        return {self.field: {self.operator: self.other}}


class Eq(BaseComparisonOperator):
    @property
    def query(self):
        return {self.field: self.other}


class GT(BaseComparisonOperator):
    operator = "$gt"


class GTE(BaseComparisonOperator):
    operator = "$gte"


class In(BaseComparisonOperator):
    operator = "$in"


class NotIn(BaseComparisonOperator):
    operator = "$nin"


class LT(BaseComparisonOperator):
    operator = "$lt"


class LTE(BaseComparisonOperator):
    operator = "$lte"


class NE(BaseComparisonOperator):
    operator = "$ne"
