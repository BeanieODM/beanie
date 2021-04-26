from beanie.odm.models import SortDirection
from beanie.odm.query_builder.operators.find.comparsion import (
    Eq,
    GT,
    GTE,
    LT,
    LTE,
    NE,
)


class CollectionField(str):
    def __getattr__(self, item):
        return CollectionField(f"{self}.{item}")

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return Eq(field=self, other=other)

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

    def __pos__(self):
        return self, SortDirection.ASCENDING

    def __neg__(self):
        return self, SortDirection.DESCENDING
