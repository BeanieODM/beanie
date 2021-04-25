from beanie.odm.query_builder.operators.find.comparsion import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NE,
)


class CollectionField:
    def __init__(self, path: str):
        self.path = path

    def __getattr__(self, item):
        return CollectionField(path=f"{self.path}.{item}")

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def __eq__(self, other):
        return EQ(field=self, other=other)

    def __gt__(self, other):
        return GT(field=self, other=other)

    def __ge__(self, other):
        return GTE(field=self, other=other)

    def __lt__(self, other):
        return LT(field=self, other=other)

    def __le__(self, other):
        return LTE(field=self, other=other)

    def __ne__(self, other):
        return NE(field=self, other=other)
