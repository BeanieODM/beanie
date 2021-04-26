from typing import Union, Optional

from pydantic import BaseModel

from beanie import Document


class D(BaseModel):
    f: float


class C(BaseModel):
    s: str
    d: D


class B(BaseModel):
    i: int
    c: C
    c_d: Union[C, D]
    o_d: Optional[D]


class A(Document):
    b: B
    i: int
    c: C
    c_d: Union[C, D]
    o_d: Optional[D]
