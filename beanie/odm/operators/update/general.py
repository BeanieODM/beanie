from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateGeneralOperator(BaseUpdateOperator):
    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class Set(BaseUpdateGeneralOperator):
    operator = "$set"


class CurrentDate(BaseUpdateGeneralOperator):
    operator = "$currentDate"


class Inc(BaseUpdateGeneralOperator):
    operator = "$inc"


class Min(BaseUpdateGeneralOperator):
    operator = "$min"


class Max(BaseUpdateGeneralOperator):
    operator = "$max"


class Mul(BaseUpdateGeneralOperator):
    operator = "$mul"


class Rename(BaseUpdateGeneralOperator):
    operator = "$rename"


class SetOnInsert(BaseUpdateGeneralOperator):
    operator = "$setOnInsert"


class Unset(BaseUpdateGeneralOperator):
    operator = "$unset"
