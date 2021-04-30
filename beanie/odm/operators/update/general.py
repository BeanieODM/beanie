from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateGeneralOperator(BaseUpdateOperator):
    """
    Base class for update query operators
    """

    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class Set(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/set/
    """

    operator = "$set"


class CurrentDate(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/currentDate/
    """

    operator = "$currentDate"


class Inc(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/inc/
    """

    operator = "$inc"


class Min(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/min/
    """

    operator = "$min"


class Max(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/max/
    """

    operator = "$max"


class Mul(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/mul/
    """

    operator = "$mul"


class Rename(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/rename/
    """

    operator = "$rename"


class SetOnInsert(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/setOnInsert/
    """

    operator = "$setOnInsert"


class Unset(BaseUpdateGeneralOperator):
    """
    MongoDB doc:
    https://docs.mongodb.com/manual/reference/operator/update/unset/
    """

    operator = "$unset"
