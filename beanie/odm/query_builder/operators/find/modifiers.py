from beanie.odm.query_builder.operators.find import BaseFindOperator


class Comment(BaseFindOperator):
    def __init__(self, field: "CollectionField", comment: str):  # noqa
        ...
