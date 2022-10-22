from typing import Generic, TypeVar, Union, Type, List

from bson import DBRef
from pydantic import BaseModel, parse_obj_as
from pydantic.fields import ModelField
from pydantic.json import ENCODERS_BY_TYPE

from beanie.odm.operators.find.comparison import (
    In,
)

T = TypeVar("T")


class Link(Generic[T]):
    def __init__(self, ref: DBRef, model_class: Type[T]):
        self.ref = ref
        self.model_class = model_class

    def fetch(self) -> Union[T, "Link"]:
        result = self.model_class.get(self.ref.id).run()  # type: ignore
        return result or self

    @classmethod
    def fetch_one(cls, link: "Link"):
        return link.fetch()

    @classmethod
    def fetch_list(cls, links: List["Link"]):
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
        return model_class.find(In("_id", ids)).to_list()  # type: ignore

    @classmethod
    def fetch_many(cls, links: List["Link"]):
        result = []
        for link in links:
            result.append(link.fetch())
        return result

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
            return model_class.validate(v)
        new_id = parse_obj_as(model_class.__fields__["id"].type_, v)
        ref = DBRef(collection=model_class.get_collection_name(), id=new_id)
        return cls(ref=ref, model_class=model_class)

    def to_ref(self):
        return self.ref

    def to_dict(self):
        return {"id": str(self.ref.id), "collection": self.ref.collection}


ENCODERS_BY_TYPE[Link] = lambda o: o.to_dict()
