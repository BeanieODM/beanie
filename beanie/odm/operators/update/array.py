from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateArrayOperator(BaseUpdateOperator):
    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class AddToSet(BaseUpdateArrayOperator):
    operator = "$addToSet"


class Pop(BaseUpdateArrayOperator):
    operator = "$pop"


class Pull(BaseUpdateArrayOperator):
    operator = "$pull"


class Push(BaseUpdateArrayOperator):
    operator = "$push"


class PullAll(BaseUpdateArrayOperator):
    operator = "$pullAll"
