from beanie.odm.operators.update import BaseUpdateOperator


class BaseUpdateArrayOperator(BaseUpdateOperator):
    """
    Base class for update array operators
    """

    operator = None

    def __init__(self, expression):
        self.expression = expression

    @property
    def query(self):
        return {self.operator: self.expression}


class AddToSet(BaseUpdateArrayOperator):
    """
    MongoDB docs:
    https://docs.mongodb.com/manual/reference/operator/update/addToSet/
    """

    operator = "$addToSet"


class Pop(BaseUpdateArrayOperator):
    """
    MongoDB docs:
    https://docs.mongodb.com/manual/reference/operator/update/pop/
    """

    operator = "$pop"


class Pull(BaseUpdateArrayOperator):
    """
    MongoDB docs:
    https://docs.mongodb.com/manual/reference/operator/update/pull/
    """

    operator = "$pull"


class Push(BaseUpdateArrayOperator):
    """
    MongoDB docs:
    https://docs.mongodb.com/manual/reference/operator/update/push/
    """

    operator = "$push"


class PullAll(BaseUpdateArrayOperator):
    """
    MongoDB docs:
    https://docs.mongodb.com/manual/reference/operator/update/pullAll/
    """

    operator = "$pullAll"
