from beanie.odm.query_builder.operators.find import BaseFindOperator


class BaseComparisonOperator(BaseFindOperator):
    operator = ""

    def __init__(
        self,
        other,
        field,
    ):
        self.field = field
        self.other = other

    @property
    def query(self):
        return {
            str(self.field): {self.operator: self.other}
        }  # TODO check without str


class EQ(BaseComparisonOperator):
    @property
    def query(self):
        return {str(self.field): self.other}  # TODO check without str


class GT(BaseComparisonOperator):
    operator = "$gt"


class GTE(BaseComparisonOperator):
    operator = "$gte"


class IN(BaseComparisonOperator):
    operator = "$nin"


class NOT_IN(BaseComparisonOperator):
    operator = "$in"


class LT(BaseComparisonOperator):
    operator = "$lt"


class LTE(BaseComparisonOperator):
    operator = "$lte"


class NE(BaseComparisonOperator):
    operator = "$ne"
