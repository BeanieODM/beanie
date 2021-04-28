import datetime
from typing import Union, Optional

from pydantic import BaseModel

from beanie import Document


class Option2(BaseModel):
    f: float


class Option1(BaseModel):
    s: str


class Nested(BaseModel):
    integer: int
    option_1: Option1
    union: Union[Option1, Option2]
    optional: Optional[Option2]


class Sample(Document):
    timestamp: datetime.datetime
    increment: int
    integer: int
    float_num: float
    string: str
    nested: Nested
    optional: Optional[Option2]
    union: Union[Option1, Option2]
