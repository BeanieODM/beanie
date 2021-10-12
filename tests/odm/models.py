import datetime
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

import pymongo
from pydantic import SecretBytes, SecretStr
from pydantic.color import Color
from pydantic import BaseModel, Field
from pymongo import IndexModel

from beanie import Document, Indexed, Insert, Replace, ValidateOnSave
from beanie.odm.actions import before_event, after_event


class Option2(BaseModel):
    f: float


class Option1(BaseModel):
    s: str


class Nested(BaseModel):
    integer: int
    option_1: Option1
    union: Union[Option1, Option2]
    optional: Optional[Option2]


class GeoObject(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]


class Sample(Document):
    timestamp: datetime.datetime
    increment: int
    integer: int
    float_num: float
    string: str
    nested: Nested
    optional: Optional[Option2]
    union: Union[Option1, Option2]
    geo: GeoObject


class SubDocument(BaseModel):
    test_str: str


class DocumentTestModel(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Settings:
        use_cache = True
        cache_expiration_time = datetime.timedelta(seconds=10)
        cache_capacity = 5
        use_state_management = True


class DocumentTestModelWithCustomCollectionName(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "custom"


class DocumentTestModelWithSimpleIndex(Document):
    test_int: Indexed(int)
    test_list: List[SubDocument]
    test_str: Indexed(str, index_type=pymongo.TEXT)


class DocumentTestModelWithIndexFlags(Document):
    test_int: Indexed(int, sparse=True)
    test_str: Indexed(str, index_type=pymongo.DESCENDING, unique=True)


class DocumentTestModelWithIndexFlagsAliases(Document):
    test_int: Indexed(int, sparse=True) = Field(alias="testInt")
    test_str: Indexed(str, index_type=pymongo.DESCENDING, unique=True) = Field(
        alias="testStr"
    )


class DocumentTestModelWithComplexIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "docs_with_index"
        indexes = [
            "test_int",
            [
                ("test_int", pymongo.ASCENDING),
                ("test_str", pymongo.DESCENDING),
            ],
            IndexModel(
                [("test_str", pymongo.DESCENDING)],
                name="test_string_index_DESCENDING",
            ),
        ]


class DocumentTestModelWithDroppedIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "docs_with_index"
        indexes = [
            "test_int",
        ]


class DocumentTestModelStringImport(Document):
    test_int: int


class DocumentTestModelFailInspection(Document):
    test_int_2: int

    class Collection:
        name = "DocumentTestModel"


class DocumentWithCustomIdUUID(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str


class DocumentWithCustomIdInt(Document):
    id: int
    name: str


class DocumentWithCustomFiledsTypes(Document):
    color: Color
    decimal: Decimal
    secret_bytes: SecretBytes
    secret_string: SecretStr
    ipv4address: IPv4Address
    ipv4interface: IPv4Interface
    ipv4network: IPv4Network
    ipv6address: IPv6Address
    ipv6interface: IPv6Interface
    ipv6network: IPv6Network
    date: datetime.date
    time: datetime.time
    timedelta: datetime.timedelta
    set_type: Set[str]
    tuple_type: Tuple[int, str]
    path: Path


class DocumentWithBsonEncodersFiledsTypes(Document):
    color: Color

    class Collection:
        bson_encoders = {Color: lambda c: c.as_rgb()}


class DocumentWithActions(Document):
    name: str
    num_1: int = 0
    num_2: int = 10
    num_3: int = 100

    @before_event(Insert)
    def capitalize_name(self):
        self.name = self.name.capitalize()

    @before_event([Insert, Replace])
    async def add_one(self):
        self.num_1 += 1

    @after_event(Insert)
    def num_2_change(self):
        self.num_2 -= 1

    @after_event(Replace)
    def num_3_change(self):
        self.num_3 -= 1


class DocumentWithTurnedOnStateManagement(Document):
    num_1: int
    num_2: int

    class Settings:
        use_state_management = True


class DocumentWithTurnedOffStateManagement(Document):
    num_1: int
    num_2: int


class DocumentWithValidationOnSave(Document):
    num_1: int
    num_2: int

    @after_event(ValidateOnSave)
    def num_2_plus_1(self):
        self.num_2 += 1

    class Settings:
        validate_on_save = True
        use_state_management = True


class DocumentWithRevisionTurnedOn(Document):
    num_1: int
    num_2: int

    class Settings:
        use_revision = True
        use_state_management = True


class DocumentWithPydanticConfig(Document):
    num_1: int

    class Config(Document.Config):
        validate_assignment = True
