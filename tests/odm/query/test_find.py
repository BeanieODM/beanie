import datetime
from enum import Enum

import pytest
from pydantic import BaseModel

from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import In
from tests.odm.models import (
    Color,
    DocumentWithBsonEncodersFiledsTypes,
    DocumentWithList,
    Door,
    House,
    Lock,
    Sample,
    Window,
)


def test_find_query():
    q = Sample.find_many(Sample.integer == 1).get_filter_query()
    assert q == {"integer": 1}

    q = Sample.find_many(
        Sample.integer == 1, Sample.nested.integer >= 2
    ).get_filter_query()
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gte": 2}}]}

    q = (
        Sample.find_many(Sample.integer == 1)
        .find_many(Sample.nested.integer >= 2)
        .get_filter_query()
    )
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gte": 2}}]}

    q = Sample.find().get_filter_query()
    assert q == {}


async def test_find_many(preset_documents):
    result = (
        await Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .to_list()
    )
    assert len(result) == 2
    for a in result:
        assert a.integer > 1
        assert a.nested.optional is None

    len_result = 0
    async for a in Sample.find_many(Sample.integer > 1).find_many(
        Sample.nested.optional == None
    ):
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_skip(preset_documents):
    q = Sample.find_many(Sample.integer > 1, skip=2)
    assert q.skip_number == 2

    q = Sample.find_many(Sample.integer > 1).skip(2)
    assert q.skip_number == 2

    result = (
        await Sample.find_many(Sample.increment > 2)
        .find_many(Sample.nested.optional == None)
        .skip(1)
        .to_list()
    )
    assert len(result) == 3
    for sample in result:
        assert sample.increment > 2
        assert sample.nested.optional is None

    len_result = 0
    async for sample in (
        Sample.find_many(Sample.increment > 2)
        .find_many(Sample.nested.optional == None)
        .skip(1)
    ):
        assert sample in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_limit(preset_documents):
    q = Sample.find_many(Sample.integer > 1, limit=2)
    assert q.limit_number == 2

    q = Sample.find_many(Sample.integer > 1).limit(2)
    assert q.limit_number == 2

    result = (
        await Sample.find_many(Sample.increment > 2)
        .find_many(Sample.nested.optional == None)
        .sort(Sample.increment)
        .limit(2)
        .to_list()
    )
    assert len(result) == 2
    for a in result:
        assert a.increment > 2
        assert a.nested.optional is None

    len_result = 0
    async for a in (
        Sample.find_many(Sample.increment > 2)
        .find(Sample.nested.optional == None)
        .sort(Sample.increment)
        .limit(2)
    ):
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_all(preset_documents):
    result = await Sample.find_all().to_list()
    assert len(result) == 10

    len_result = 0
    async for a in Sample.find_all():
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_one(preset_documents):
    a = await Sample.find_one(Sample.integer > 1).find_one(
        Sample.nested.optional == None
    )
    assert a.integer > 1
    assert a.nested.optional is None

    a = await Sample.find_one(Sample.integer > 100).find_one(
        Sample.nested.optional == None
    )
    assert a is None


async def test_get(preset_documents):
    a = await Sample.find_one(Sample.integer > 1).find_one(
        Sample.nested.optional == None
    )
    assert a.integer > 1
    assert a.nested.optional is None

    new_a = await Sample.get(a.id)
    assert new_a == a

    # check for another type
    new_a = await Sample.get(str(a.id))
    assert new_a == a


async def test_sort(preset_documents):
    q = Sample.find_many(Sample.integer > 1, sort="-integer")
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    q = Sample.find_many(Sample.integer > 1, sort="integer")
    assert q.sort_expressions == [("integer", SortDirection.ASCENDING)]

    q = Sample.find_many(Sample.integer > 1).sort("-integer")
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    q = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.integer < 100)
        .sort("-integer")
    )
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    result = await Sample.find_many(
        Sample.integer > 1, sort="-integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf >= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort="+integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf <= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort="integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf <= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort=-Sample.integer
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf >= a.integer
        i_buf = a.integer

    result = (
        await Sample.find_many(Sample.integer > 1)
        .sort([Sample.const, -Sample.integer])
        .to_list()
    )
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf >= a.integer
        i_buf = a.integer

    with pytest.raises(TypeError):
        Sample.find_many(Sample.integer > 1, sort=1)


async def test_find_many_with_projection(preset_documents):
    class SampleProjection(BaseModel):
        string: str
        integer: int

    result = (
        await Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .project(projection_model=SampleProjection)
        .to_list()
    )
    assert result == [
        SampleProjection(string="test_2", integer=2),
        SampleProjection(string="test_2", integer=2),
    ]

    result = (
        await Sample.find_many(Sample.integer > 1)
        .find_many(
            Sample.nested.optional == None, projection_model=SampleProjection
        )
        .to_list()
    )
    assert result == [
        SampleProjection(string="test_2", integer=2),
        SampleProjection(string="test_2", integer=2),
    ]


async def test_find_many_with_custom_projection(preset_documents):
    class SampleProjection(BaseModel):
        string: str
        i: int

        class Settings:
            projection = {"string": 1, "i": "$nested.integer"}

    result = (
        await Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .project(projection_model=SampleProjection)
        .sort(Sample.nested.integer)
        .to_list()
    )
    assert result == [
        SampleProjection(string="test_2", i=3),
        SampleProjection(string="test_2", i=4),
    ]


async def test_find_many_with_session(preset_documents, session):
    q_1 = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.nested.optional == None)
        .set_session(session)
    )
    assert q_1.session == session

    q_2 = Sample.find_many(Sample.integer > 1).find_many(
        Sample.nested.optional == None, session=session
    )
    assert q_2.session == session

    result = await q_2.to_list()

    assert len(result) == 2
    for a in result:
        assert a.integer > 1
        assert a.nested.optional is None

    len_result = 0
    async for a in Sample.find_many(Sample.integer > 1).find_many(
        Sample.nested.optional == None
    ):
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_bson_encoders_filed_types():
    custom = DocumentWithBsonEncodersFiledsTypes(
        color="7fffd4",
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    c = await custom.insert()
    c_fromdb = await DocumentWithBsonEncodersFiledsTypes.find_one(
        DocumentWithBsonEncodersFiledsTypes.color == Color("7fffd4")
    )
    assert c_fromdb.color.as_hex() == c.color.as_hex()


async def test_find_by_datetime(preset_documents):
    datetime_1 = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) - datetime.timedelta(days=7)
    datetime_2 = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) - datetime.timedelta(days=2)
    docs = await Sample.find(
        Sample.timestamp >= datetime_1,
        Sample.timestamp <= datetime_2,
    ).to_list()
    assert len(docs) == 5


async def test_find_first_or_none(preset_documents):
    q = Sample.find(Sample.increment > 1).sort(-Sample.increment)
    doc = await q.first_or_none()
    assert doc is not None
    assert doc.increment == 9

    docs = await q.to_list()
    assert len(docs) == 8

    doc = (
        await Sample.find(Sample.increment > 9)
        .sort(-Sample.increment)
        .first_or_none()
    )
    assert doc is None


async def test_find_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        await Sample.find_many(Sample.increment > 1, wrong=100).to_list()

    await Sample.find_many(
        Sample.increment > 1, Sample.integer > 1, allow_disk_use=True
    ).to_list()

    await Sample.find_many(
        Sample.increment > 1, Sample.integer > 1, hint="integer_1"
    ).to_list()

    await House.find_many(
        House.height > 1, fetch_links=True, hint="height_1"
    ).to_list()

    await House.find_many(
        House.height > 1, fetch_links=True, allowDiskUse=True
    ).to_list()

    await Sample.find_one(
        Sample.increment > 1, Sample.integer > 1, hint="integer_1"
    )

    await House.find_one(House.height > 1, fetch_links=True, hint="height_1")


def test_find_clone():
    q = (
        Sample.find_many(Sample.integer == 1)
        .find_many(Sample.nested.integer >= 2)
        .sort(Sample.integer)
        .limit(100)
    )

    new_q = q.clone()
    new_q.find(Sample.nested.integer >= 100).sort(Sample.string).limit(10)

    assert q.get_filter_query() == {
        "$and": [{"integer": 1}, {"nested.integer": {"$gte": 2}}]
    }
    assert q.sort_expressions == [("integer", SortDirection.ASCENDING)]
    assert q.limit_number == 100
    assert new_q.get_filter_query() == {
        "$and": [
            {"integer": 1},
            {"nested.integer": {"$gte": 2}},
            {"nested.integer": {"$gte": 100}},
        ]
    }
    assert new_q.sort_expressions == [
        ("integer", SortDirection.ASCENDING),
        ("string", SortDirection.ASCENDING),
    ]
    assert new_q.limit_number == 10


async def test_find_many_with_enum_in_query(preset_documents):
    class TestEnum(str, Enum):
        INTEGER = Sample.integer
        SAMPLE_NESTED_OPTIONAL = Sample.nested.optional
        CONST = "const"
        CONST_VALUE = "TEST"

    filter_query = {
        TestEnum.INTEGER: {"$gt": 1},
        TestEnum.SAMPLE_NESTED_OPTIONAL: {"$type": "null"},
        TestEnum.CONST: TestEnum.CONST_VALUE,
    }
    result = await Sample.find_many(filter_query).to_list()
    assert len(result) == 2


# @pytest.mark.asyncio
async def test_fetch_links_with_chained_delete():
    lock = await Lock(k=123).insert()
    window = await Window(x=1, y=2, lock=lock).insert()
    door = await Door(t=10, window=window, locks=[lock]).insert()

    await House(windows=[window], door=door, height=10, name="test").insert()
    await House(windows=[window], door=door, height=12, name="test2").insert()

    # Deletion with chained query and fetch_links
    deleted_count = (
        await House.find(House.height > 5, fetch_links=True)
        .find(House.height < 20)
        .delete()
    )

    assert deleted_count.deleted_count == 2

    # Confirm deletion
    remaining = await House.find_all().to_list()
    assert len(remaining) == 0


async def test_distinct(preset_documents):
    # distinct without filter
    values = await Sample.find().distinct("integer")
    assert sorted(values) == [0, 1, 2, 3]

    # distinct with filter
    values = await Sample.find(Sample.integer > 1).distinct("integer")
    assert sorted(values) == [2, 3]

    # distinct on string field
    values = await Sample.find(Sample.integer == 0).distinct("string")
    assert values == ["test_0"]

    # empty result
    values = await Sample.find(Sample.integer == 999).distinct("string")
    assert values == []

    # skip/limit should be ignored by distinct (MongoDB does not support them)
    values = await Sample.find().skip(5).limit(2).distinct("integer")
    assert sorted(values) == [0, 1, 2, 3]


async def test_distinct_with_beanie_operators(preset_documents):
    # In operator
    values = await Sample.find(In(Sample.integer, [0, 2])).distinct("integer")
    assert sorted(values) == [0, 2]

    # NE operator
    values = await Sample.find(Sample.integer != 0).distinct("integer")
    assert sorted(values) == [1, 2, 3]


async def test_distinct_with_session(preset_documents, session):
    values = await Sample.find(Sample.integer > 1).distinct(
        "integer", session=session
    )
    assert sorted(values) == [2, 3]


async def test_distinct_chained_find(preset_documents):
    # Multiple find() chaining before distinct
    values = (
        await Sample.find(Sample.integer >= 1)
        .find(Sample.integer <= 2)
        .distinct("integer")
    )
    assert sorted(values) == [1, 2]


async def test_distinct_nested_field(preset_documents):
    values = await Sample.find(Sample.integer == 0).distinct("nested.integer")
    assert sorted(values) == [0, 1]


async def test_distinct_with_fetch_links():
    lock1 = await Lock(k=1).insert()
    lock2 = await Lock(k=2).insert()
    window1 = await Window(x=1, y=1, lock=lock1).insert()
    window2 = await Window(x=2, y=2, lock=lock2).insert()
    door = await Door(t=10, window=window1, locks=[lock1, lock2]).insert()

    await House(
        windows=[window1], door=door, height=10, name="house_a"
    ).insert()
    await House(
        windows=[window2], door=door, height=20, name="house_b"
    ).insert()
    await House(
        windows=[window1, window2], door=door, height=10, name="house_c"
    ).insert()

    # distinct on own field with fetch_links
    names = await House.find(House.height == 10, fetch_links=True).distinct(
        "name"
    )
    assert sorted(names) == ["house_a", "house_c"]

    # distinct on linked document field with fetch_links
    heights = await House.find(House.door.t == 10, fetch_links=True).distinct(
        "height"
    )
    assert sorted(heights) == [10, 20]

    # skip/limit/sort should be ignored by distinct even with fetch_links
    names = (
        await House.find(fetch_links=True)
        .sort("name")
        .skip(1)
        .limit(1)
        .distinct("name")
    )
    assert sorted(names) == ["house_a", "house_b", "house_c"]


async def test_distinct_array_field():
    await DocumentWithList(list_values=["a", "b"]).insert()
    await DocumentWithList(list_values=["b", "c"]).insert()
    await DocumentWithList(list_values=["c", "d"]).insert()

    # distinct on an array field should return individual elements, not arrays
    values = await DocumentWithList.find().distinct("list_values")
    assert sorted(values) == ["a", "b", "c", "d"]
