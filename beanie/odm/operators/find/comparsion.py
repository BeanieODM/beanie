from beanie.odm.operators.find import BaseFindOperator


class BaseFindComparisonOperator(BaseFindOperator):
    """
    Base class for find query comparison operators
    """

    operator = ""

    def __init__(
        self,
        field,
        other,
    ):
        """

        :param field: Union[str, ExpressionField]
        :param other:
        """
        self.field = field
        self.other = other

    @property
    def query(self):
        return {self.field: {self.operator: self.other}}


class Eq(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/eq/
    """

    @property
    def query(self):
        return {self.field: self.other}


class GT(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/gt/
    """

    operator = "$gt"


class GTE(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/gte/
    """

    operator = "$gte"


class In(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/in/
    """

    operator = "$in"


class NotIn(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/nin/
    """

    operator = "$nin"


class LT(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/lt/
    """

    operator = "$lt"


class LTE(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/lte/
    """

    operator = "$lte"


class NE(BaseFindComparisonOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/query/ne/
    """

    operator = "$ne"
