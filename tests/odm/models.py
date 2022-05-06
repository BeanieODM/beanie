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
from beanie.odm.actions import before_event, after_event, Delete
from beanie.odm.fields import Link
from beanie.odm.settings.timeseries import TimeSeriesConfig
from beanie.odm.union_doc import UnionDoc


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
    increment: Indexed(int)
    integer: Indexed(int)
    float_num: float
    string: str
    nested: Nested
    optional: Optional[Option2]
    union: Union[Option1, Option2]
    geo: GeoObject


class SubDocument(BaseModel):
    test_str: str
    test_int: int = 42


class DocumentTestModel(Document):
    test_int: int
    test_list: List[SubDocument] = Field(hidden=True)
    test_doc: SubDocument
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

    # class Settings:
    #     name = "custom"


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

    # class Settings:
    #     name = "docs_with_index"
    #     indexes = [
    #         "test_int",
    #         [
    #             ("test_int", pymongo.ASCENDING),
    #             ("test_str", pymongo.DESCENDING),
    #         ],
    #         IndexModel(
    #             [("test_str", pymongo.DESCENDING)],
    #             name="test_string_index_DESCENDING",
    #         ),
    #     ]


class DocumentTestModelWithDroppedIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "docs_with_index"
        indexes = [
            "test_int",
        ]

    class Settings:
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

    class Settings:
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
    timedelta: datetime.timedelta
    set_type: Set[str]
    tuple_type: Tuple[int, str]
    path: Path


class DocumentWithBsonEncodersFiledsTypes(Document):
    color: Color
    timestamp: datetime.datetime

    class Settings:
        bson_encoders = {
            Color: lambda c: c.as_rgb(),
            datetime.datetime: lambda o: o.isoformat(timespec="microseconds"),
        }


class DocumentWithActions(Document):
    name: str
    num_1: int = 0
    num_2: int = 10
    num_3: int = 100

    class Inner:
        inner_num_1 = 0
        inner_num_2 = 0

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

    @before_event(Delete)
    def inner_num_to_one(self):
        self.Inner.inner_num_1 = 1

    @after_event(Delete)
    def inner_num_to_two(self):
        self.Inner.inner_num_2 = 2


class InheritedDocumentWithActions(DocumentWithActions):
    ...


class InternalDoc(BaseModel):
    num: int = 100
    string: str = "test"
    lst: List[int] = [1, 2, 3, 4, 5]


class DocumentWithTurnedOnStateManagement(Document):
    num_1: int
    num_2: int
    internal: InternalDoc

    class Settings:
        use_state_management = True


class DocumentWithTurnedOnReplaceObjects(Document):
    num_1: int
    num_2: int
    internal: InternalDoc

    class Settings:
        use_state_management = True
        state_management_replace_objects = True


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


class Window(Document):
    x: int
    y: int


class Door(Document):
    t: int = 10


class Roof(Document):
    r: int = 100


class House(Document):
    windows: List[Link[Window]]
    door: Link[Door]
    roof: Optional[Link[Roof]]
    name: Indexed(str) = Field(hidden=True)
    height: Indexed(int) = 2


class DocumentForEncodingTest(Document):
    bytes_field: Optional[bytes]
    datetime_field: Optional[datetime.datetime]


class DocumentWithTimeseries(Document):
    ts: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Settings:
        timeseries = TimeSeriesConfig(time_field="ts", expire_after_seconds=2)


class DocumentForEncodingTestDate(Document):
    date_field: datetime.date = Field(default_factory=datetime.date.today)

    class Settings:
        name = "test_date"
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=0,
                minute=0,
                second=0,
            )
        }


class DocumentUnion(UnionDoc):
    class Settings:
        name = "multi_model"


class DocumentMultiModelOne(Document):
    int_filed: int = 0
    shared: int = 0

    class Settings:
        union_doc = DocumentUnion


class DocumentMultiModelTwo(Document):
    str_filed: str = "test"
    shared: int = 0
    linked_doc: Optional[Link[DocumentMultiModelOne]] = None

    class Settings:
        union_doc = DocumentUnion
