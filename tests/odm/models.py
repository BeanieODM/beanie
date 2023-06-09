import datetime
import decimal
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
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

import pydantic
import pymongo
from pydantic import (
    BaseModel,
    Extra,
    Field,
    PrivateAttr,
    SecretBytes,
    SecretStr,
    condecimal,
)
from pydantic.color import Color
from pymongo import IndexModel

from beanie import (
    Document,
    Indexed,
    Insert,
    Replace,
    Update,
    ValidateOnSave,
    Save,
)
from beanie.odm.actions import Delete, after_event, before_event
from beanie.odm.fields import Link, PydanticObjectId, BackLink
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
    const: str = "TEST"


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


class DocumentTestModelWithLink(Document):
    test_link: Link[DocumentTestModel]

    class Settings:
        use_cache = True
        cache_expiration_time = datetime.timedelta(seconds=10)
        cache_capacity = 5
        use_state_management = True


class DocumentTestModelWithCustomCollectionName(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Settings:
        name = "custom"
        class_id = "different_class_id"


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

    class Settings:
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

    class Settings:
        name = "docs_with_index"
        indexes = [
            "test_int",
        ]


class DocumentTestModelStringImport(Document):
    test_int: int


class DocumentTestModelFailInspection(Document):
    test_int_2: int

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
    _private_num: int = PrivateAttr(default=100)

    class Inner:
        inner_num_1 = 0
        inner_num_2 = 0

    @before_event(Insert)
    def capitalize_name(self):
        self.name = self.name.capitalize()

    @before_event([Insert, Replace, Save])
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

    @before_event(Update)
    def inner_num_to_one_2(self):
        self._private_num += 1

    @after_event(Update)
    def inner_num_to_two_2(self):
        self.num_2 -= 1


class DocumentWithActions2(Document):
    name: str
    num_1: int = 0
    num_2: int = 10
    num_3: int = 100
    _private_num: int = PrivateAttr(default=100)

    class Inner:
        inner_num_1 = 0
        inner_num_2 = 0

    @before_event(Insert)
    def capitalize_name(self):
        self.name = self.name.capitalize()

    @before_event(Insert, Replace, Save)
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

    @before_event(Update)
    def inner_num_to_one_2(self):
        self._private_num += 1

    @after_event(Update)
    def inner_num_to_two_2(self):
        self.num_2 -= 1


class InheritedDocumentWithActions(DocumentWithActions):
    ...


class InternalDoc(BaseModel):
    _private_field: str = PrivateAttr(default="TEST_PRIVATE")
    num: int = 100
    string: str = "test"
    lst: List[int] = [1, 2, 3, 4, 5]

    def change_private(self):
        self._private_field = "PRIVATE_CHANGED"

    def get_private(self):
        return self._private_field


class DocumentWithTurnedOnStateManagement(Document):
    num_1: int
    num_2: int
    internal: InternalDoc

    class Settings:
        use_state_management = True


class DocumentWithTurnedOnStateManagementWithCustomId(Document):
    id: int
    num_1: int
    num_2: int

    class Settings:
        use_state_management = True


class DocumentWithTurnedOnReplaceObjects(Document):
    num_1: int
    num_2: int
    internal: InternalDoc

    class Settings:
        use_state_management = True
        state_management_replace_objects = True


class DocumentWithTurnedOnSavePrevious(Document):
    num_1: int
    num_2: int
    internal: InternalDoc

    class Settings:
        use_state_management = True
        state_management_save_previous = True


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


class DocumentWithExtras(Document):
    num_1: int

    class Config(Document.Config):
        extra = Extra.allow


class DocumentWithExtrasKw(Document, extra=Extra.allow):
    num_1: int


class Yard(Document):
    v: int
    w: int


class Lock(Document):
    k: int


class Window(Document):
    x: int
    y: int
    lock: Optional[Link[Lock]]


class Door(Document):
    t: int = 10
    window: Optional[Link[Window]]
    locks: Optional[List[Link[Lock]]]


class Roof(Document):
    r: int = 100


class House(Document):
    windows: List[Link[Window]]
    door: Link[Door]
    roof: Optional[Link[Roof]]
    yards: Optional[List[Link[Yard]]]
    name: Indexed(str) = Field(hidden=True)
    height: Indexed(int) = 2

    class Config:
        extra = Extra.allow


class DocumentForEncodingTest(Document):
    bytes_field: Optional[bytes]
    datetime_field: Optional[datetime.datetime]


class DocumentWithTimeseries(Document):
    ts: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Settings:
        timeseries = TimeSeriesConfig(time_field="ts", expire_after_seconds=2)


class DocumentWithStringField(Document):
    string_field: str


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
        class_id = "123"


class DocumentMultiModelOne(Document):
    int_filed: int = 0
    shared: int = 0

    class Settings:
        union_doc = DocumentUnion
        name = "multi_one"
        class_id = "123"


class DocumentMultiModelTwo(Document):
    str_filed: str = "test"
    shared: int = 0
    linked_doc: Optional[Link[DocumentMultiModelOne]] = None

    class Settings:
        union_doc = DocumentUnion
        name = "multi_two"
        class_id = "123"


class YardWithRevision(Document):
    v: int
    w: int

    class Settings:
        use_revision = True
        use_state_management = True


class LockWithRevision(Document):
    k: int

    class Settings:
        use_revision = True
        use_state_management = True


class WindowWithRevision(Document):
    x: int
    y: int
    lock: Link[LockWithRevision]

    class Settings:
        use_revision = True
        use_state_management = True


class HouseWithRevision(Document):
    windows: List[Link[WindowWithRevision]]

    class Settings:
        use_revision = True
        use_state_management = True


# classes for inheritance test
class Vehicle(Document):
    """Root parent for testing flat inheritance"""

    #               Vehicle
    #              /   |   \
    #             /    |    \
    #        Bicycle  Bike  Car
    #                         \
    #                          \
    #                          Bus
    color: str

    @after_event(Insert)
    def on_object_create(self):
        # this event will be triggered for all children too (self will have corresponding type)
        ...

    class Settings:
        is_root = True


class Bicycle(Vehicle):
    frame: int
    wheels: int


class Fuelled(BaseModel):
    """Just a mixin"""

    fuel: Optional[str]


class Car(Vehicle, Fuelled):
    body: str


class Bike(Vehicle, Fuelled):
    ...


class Bus(Car, Fuelled):
    seats: int


class Owner(Document):
    name: str
    vehicles: List[Link[Vehicle]] = []


class MixinNonRoot(BaseModel):
    id: int = Field(..., ge=1, le=254)


class MyDocNonRoot(Document):
    class Settings:
        use_state_management = True


class TestNonRoot(MixinNonRoot, MyDocNonRoot):
    name: str


class Test2NonRoot(MyDocNonRoot):
    name: str


class Child(BaseModel):
    child_field: str


class SampleWithMutableObjects(Document):
    d: Dict[str, Child]
    lst: List[Child]


class SampleLazyParsing(Document):
    i: int
    s: str
    lst: List[int] = Field(
        [],
    )

    class Settings:
        lazy_parsing = True
        use_state_management = True

    class Config:
        validate_assignment = True


class RootDocument(Document):
    name: str
    link_root: Link[Document]


class ADocument(RootDocument):
    surname: str
    link_a: Link[Document]

    class Settings:
        name = "B"


class BDocument(RootDocument):
    email: str
    link_b: Link[Document]

    class Settings:
        name = "B"


class StateAndDecimalFieldModel(Document):
    amt: decimal.Decimal
    other_amt: condecimal(
        decimal_places=1, multiple_of=decimal.Decimal("0.5")
    ) = 0

    class Settings:
        name = "amounts"
        use_revision = True
        use_state_management = True


class Region(Document):
    state: Optional[str] = "TEST"
    city: Optional[str] = "TEST"
    district: Optional[str] = "TEST"


class UsersAddresses(Document):
    region_id: Optional[Link[Region]]
    phone_number: Optional[str] = None
    street: Optional[str] = None


class AddressView(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    phone_number: Optional[str]
    street: Optional[str]
    state: Optional[str]
    city: Optional[str]
    district: Optional[str]

    class Settings:
        projection = {
            "id": "$_id",
            "phone_number": 1,
            "street": 1,
            "sub_district": "$region_id.sub_district",
            "city": "$region_id.city",
            "state": "$region_id.state",
        }


class SelfLinked(Document):
    item: Optional[Link["SelfLinked"]]
    s: str


class LoopedLinksA(Document):
    b: "LoopedLinksB"


class LoopedLinksB(Document):
    a: Optional[LoopedLinksA]


class DocWithCollectionInnerClass(Document):
    s: str

    class Collection:
        name = "test"


class DocumentWithDecimalField(Document):
    amt: decimal.Decimal
    other_amt: pydantic.condecimal(
        decimal_places=1, multiple_of=decimal.Decimal("0.5")
    ) = 0

    class Config:
        validate_assignment = True

    class Settings:
        name = "amounts"
        use_revision = True
        use_state_management = True
        indexes = [
            pymongo.IndexModel(
                keys=[("amt", pymongo.ASCENDING)], name="amt_ascending"
            ),
            pymongo.IndexModel(
                keys=[("other_amt", pymongo.DESCENDING)],
                name="other_amt_descending",
            ),
        ]


class ModelWithOptionalField(BaseModel):
    s: Optional[str]
    i: int


class DocumentWithKeepNullsFalse(Document):
    o: Optional[str]
    m: ModelWithOptionalField

    class Settings:
        keep_nulls = False
        use_state_management = True


class ReleaseElemMatch(BaseModel):
    major_ver: int
    minor_ver: int
    build_ver: int


class PackageElemMatch(Document):
    releases: List[ReleaseElemMatch] = []


class DocumentWithLink(Document):
    link: Link["DocumentWithBackLink"]
    s: str = "TEST"


class DocumentWithBackLink(Document):
    back_link: BackLink[DocumentWithLink] = Field(original_field="link")
    i: int = 1


class DocumentWithListLink(Document):
    link: List[Link["DocumentWithListBackLink"]]
    s: str = "TEST"


class DocumentWithListBackLink(Document):
    back_link: List[BackLink[DocumentWithListLink]] = Field(
        original_field="link"
    )
    i: int = 1


class DocumentToBeLinked(Document):
    s: str = "TEST"


class DocumentWithListOfLinks(Document):
    links: List[Link[DocumentToBeLinked]]
    s: str = "TEST"


class DocumentWithTimeStampToTestConsistency(Document):
    ts: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class DocumentWithIndexMerging1(Document):
    class Settings:
        indexes = [
            "s1",
            [
                ("s2", pymongo.ASCENDING),
            ],
            IndexModel(
                [("s3", pymongo.ASCENDING)],
                name="s3_index",
            ),
            IndexModel(
                [("s4", pymongo.ASCENDING)],
                name="s4_index",
            ),
        ]


class DocumentWithIndexMerging2(DocumentWithIndexMerging1):
    class Settings:
        merge_indexes = True
        indexes = [
            "s0",
            "s1",
            [
                ("s2", pymongo.DESCENDING),
            ],
            IndexModel(
                [("s3", pymongo.DESCENDING)],
                name="s3_index",
            ),
        ]
