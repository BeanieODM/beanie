import asyncio
from enum import Enum
from typing import Dict, Generic, TypeVar, Union, Type, List, Optional

from bson import ObjectId, DBRef
from bson.errors import InvalidId
from pydantic import BaseModel, parse_obj_as
from pydantic.fields import ModelField
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
    In,
)
from beanie.odm.utils.parsing import parse_obj


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
    def __getitem__(self, item):
        """
        Get sub field

        :param item: name of the subfield
        :return: ExpressionField
        """
        return ExpressionField(f"{self}.{item}")

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
        if isinstance(other, ExpressionField):
            return super(ExpressionField, self).__eq__(other)
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

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class DeleteRules(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    DELETE_LINKS = "DELETE_LINKS"


class WriteRules(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    WRITE = "WRITE"


class LinkTypes(str, Enum):
    DIRECT = "DIRECT"
    OPTIONAL_DIRECT = "OPTIONAL_DIRECT"
    LIST = "LIST"
    OPTIONAL_LIST = "OPTIONAL_LIST"


class LinkInfo(BaseModel):
    field: str
    model_class: Type[BaseModel]  # Document class
    link_type: LinkTypes
    nested_links: Optional[Dict]


T = TypeVar("T")


class Link(Generic[T]):
    def __init__(self, ref: DBRef, model_class: Type[T]):
        self.ref = ref
        self.model_class = model_class

    async def fetch(self, fetch_links: bool = False) -> Union[T, "Link"]:
        result = await self.model_class.get(self.ref.id, with_children=True, fetch_links=fetch_links)  # type: ignore
        return result or self

    @classmethod
    async def fetch_one(cls, link: "Link"):
        return await link.fetch()

    @classmethod
    async def fetch_list(cls, links: List["Link"], fetch_links: bool = False):
        ids = []
        model_class = None
        for link in links:
            if model_class is None:
                model_class = link.model_class
            else:
                if model_class != link.model_class:
                    raise ValueError(
                        "All the links must have the same model class"
                    )
            ids.append(link.ref.id)
        return await model_class.find(In("_id", ids), with_children=True, fetch_links=fetch_links).to_list()  # type: ignore

    @classmethod
    async def fetch_many(cls, links: List["Link"]):
        coros = []
        for link in links:
            coros.append(link.fetch())
        return await asyncio.gather(*coros)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[DBRef, T], field: ModelField):
        model_class = field.sub_fields[0].type_  # type: ignore
        if isinstance(v, DBRef):
            return cls(ref=v, model_class=model_class)
        if isinstance(v, Link):
            return v
        if isinstance(v, dict) or isinstance(v, BaseModel):
            return parse_obj(model_class, v)
        new_id = parse_obj_as(model_class.__fields__["id"].type_, v)
        ref = DBRef(collection=model_class.get_collection_name(), id=new_id)
        return cls(ref=ref, model_class=model_class)

    def to_ref(self):
        return self.ref

    def to_dict(self):
        return {"id": str(self.ref.id), "collection": self.ref.collection}


ENCODERS_BY_TYPE[Link] = lambda o: o.to_dict()
