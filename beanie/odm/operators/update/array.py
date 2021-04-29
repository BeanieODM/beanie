from beanie.odm.operators.update import BaseUpdateOperator


class BaseArrayUpdateOperator(BaseUpdateOperator):
    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class AddToSet(BaseArrayUpdateOperator):
    operator = "$addToSet"


class Pop(BaseArrayUpdateOperator):
    operator = "$pop"


class Pull(BaseArrayUpdateOperator):
    operator = "$pull"


class Push(BaseArrayUpdateOperator):
    operator = "$push"


class PullAll(BaseArrayUpdateOperator):
    operator = "$pullAll"
