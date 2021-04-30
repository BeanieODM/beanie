from beanie.odm.operators.find import BaseFindOperator


class BaseFindComparisonOperator(BaseFindOperator):
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


class Eq(BaseFindComparisonOperator):
    @property
    def query(self):
        return {self.field: self.other}


class GT(BaseFindComparisonOperator):
    operator = "$gt"


class GTE(BaseFindComparisonOperator):
    operator = "$gte"


class In(BaseFindComparisonOperator):
    operator = "$in"


class NotIn(BaseFindComparisonOperator):
    operator = "$nin"


class LT(BaseFindComparisonOperator):
    operator = "$lt"


class LTE(BaseFindComparisonOperator):
    operator = "$lte"


class NE(BaseFindComparisonOperator):
    operator = "$ne"
