from beanie.odm.query_builder.operators.update import BaseUpdateOperator


class BaseGeneralUpdateOperator(BaseUpdateOperator):
    operator = None

    def __init__(self, expression):
        self.expression = expression

    def query(self):
        return {self.operator: self.expression}


class Set(BaseGeneralUpdateOperator):
    operator = "$set"


class CurrentDate(BaseGeneralUpdateOperator):
    operator = "$currentDate"


class Inc(BaseGeneralUpdateOperator):
    operator = "$inc"


class Min(BaseGeneralUpdateOperator):
    operator = "$min"


class Max(BaseGeneralUpdateOperator):
    operator = "$max"


class Mul(BaseGeneralUpdateOperator):
    operator = "$mul"


class Rename(BaseGeneralUpdateOperator):
    operator = "$rename"


class SetOnInsert(BaseGeneralUpdateOperator):
    operator = "$setOnInsert"


class Unset(BaseGeneralUpdateOperator):
    operator = "$unset"
