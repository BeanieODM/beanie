from bson import ObjectId
from bson.errors import InvalidId
from pydantic.json import ENCODERS_BY_TYPE
from pymongo import ASCENDING

from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import (
    Eq,
    GT,
    GTE,
    LT,
    LTE,
    NE,
)


def Indexed(typ, index_type=ASCENDING, **kwargs):
    """
    Returns a subclass of `typ` with an extra attribute `_indexed` as a tuple:
    - Index 0: `index_type` such as `pymongo.ASCENDING`
    - Index 1: `kwargs` passed to `IndexModel`
    When instantiated the type of the result will actually be `typ`.
    """

    class NewType(typ):
        _indexed = (index_type, kwargs)

        def __new__(cls, *args, **kwargs):
            return typ.__new__(typ, *args, **kwargs)

    NewType.__name__ = f"Indexed {typ.__name__}"
    return NewType


class PydanticObjectId(ObjectId):
    """
    Object Id field. Compatible with Pydantic.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        try:
            return PydanticObjectId(v)
        except InvalidId:
            raise TypeError("Id must be of type PydanticObjectId")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            examples=["5eb7cf5a86d9755df3a6c593", "5eb7cfb05e32e07750a1756a"],
        )


ENCODERS_BY_TYPE[
    PydanticObjectId
] = str  # it is a workaround to force pydantic make json schema for this field


class ExpressionField(str):
    def __getattr__(self, item):
        """
        Get sub field

        :param item: name of the subfield
        :return: ExpressionField
        """
        return ExpressionField(f"{self}.{item}")

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
