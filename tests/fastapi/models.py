from typing import List

from pydantic import Field

from beanie import Document, Indexed, Link
from beanie.odm.fields import BackLink
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2


class WindowAPI(Document):
    x: int
    y: int


class DoorAPI(Document):
    t: int = 10


class RoofAPI(Document):
    r: int = 100


class HouseAPI(Document):
    windows: List[Link[WindowAPI]]
    name: Indexed(str)
    height: Indexed(int) = 2


class House(Document):
    name: str
    owner: Link["Person"]


class Person(Document):
    name: str
    house: BackLink[House] = (
        Field(json_schema_extra={"original_field": "owner"})
        if IS_PYDANTIC_V2
        else Field(original_field="owner")
    )
