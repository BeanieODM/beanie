import datetime
from enum import Enum

import pytest
from pydantic import BaseModel

from beanie.exceptions import DocumentWasPartiallyLoaded
from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import In
from beanie.odm.utils.projection import get_exclusion_model
from beanie.odm.utils.pydantic import get_model_fields
from tests.odm.models import (
    Bicycle,
    Color,
    DocumentMultiModelOne,
    DocumentTestModel,
    DocumentUnion,
    DocumentWithBsonEncodersFiledsTypes,
    DocumentWithList,
    DocumentWithNestedAlias,
    Door,
    House,
    Lock,
    Sample,
    Vehicle,
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


# --- Exclusion projection tests ---


async def test_find_many_with_exclude(preset_documents):
    """Basic exclusion: excluded fields become None, others are populated.
    Also verifies that ExpressionField references work as arguments."""
    # String field names
    result = (
        await Sample.find_many(Sample.integer == 0)
        .exclude("float_num", "geo")
        .to_list()
    )
    assert len(result) > 0
    for doc in result:
        assert isinstance(doc, Sample)
        assert doc.string == "test_0"
        assert doc.integer == 0
        assert doc.float_num is None
        assert doc.geo is None

    # ExpressionField references (Sample.field_name)
    result2 = (
        await Sample.find_many(Sample.integer == 0)
        .exclude(Sample.float_num, Sample.geo)
        .to_list()
    )
    assert len(result2) > 0
    for doc in result2:
        assert isinstance(doc, Sample)
        assert doc.float_num is None
        assert doc.geo is None


async def test_find_one_with_exclude(preset_documents):
    """Exclusion works with find_one."""
    doc = await Sample.find_one(Sample.integer == 0).exclude("float_num")
    assert doc is not None
    assert isinstance(doc, Sample)
    assert doc.string == "test_0"
    assert doc.integer == 0
    assert doc.float_num is None


def test_exclude_with_project_raises():
    """Using exclude() and project() together raises ValueError."""

    class SampleProjection(BaseModel):
        string: str
        integer: int

    with pytest.raises(
        ValueError, match=r"Cannot use exclude.*together with project"
    ):
        Sample.find_many(Sample.integer == 0).project(
            projection_model=SampleProjection
        ).exclude("float_num")

    with pytest.raises(
        ValueError, match=r"Cannot use project.*together with exclude"
    ):
        Sample.find_many(Sample.integer == 0).exclude("float_num").project(
            projection_model=SampleProjection
        )


async def test_exclude_with_fetch_links():
    """fetch_links runs through an aggregation pipeline, so exclusion is
    applied with $unset rather than a projection."""
    lock = await Lock(k=10).insert()
    window = await Window(x=1, y=2, lock=lock).insert()
    door = await Door(t=5, window=window, locks=[lock]).insert()
    await House(
        windows=[window], door=door, height=100, name="test_exclude"
    ).insert()

    many = (
        await House.find(House.name == "test_exclude", fetch_links=True)
        .exclude("height")
        .to_list()
    )
    assert len(many) == 1
    assert isinstance(many[0], House)
    assert many[0].name == "test_exclude"
    assert many[0].height is None
    assert many[0].door.t == 5

    one = await House.find_one(
        House.name == "test_exclude", fetch_links=True
    ).exclude("height")
    assert isinstance(one, House)
    assert one.name == "test_exclude"
    assert one.height is None


def test_exclude_clone():
    """Cloning a query preserves _exclude_fields."""
    q = Sample.find_many(Sample.integer == 1).exclude("float_num", "geo")
    cloned = q.clone()

    assert cloned._exclude_fields == ["float_num", "geo"]
    # Modifying the clone should not affect the original
    cloned._exclude_fields = []
    cloned.exclude("string")
    assert q._exclude_fields == ["float_num", "geo"]
    assert cloned._exclude_fields == ["string"]


def test_exclude_accumulates():
    """Multiple .exclude() calls accumulate fields, not replace."""
    q = (
        Sample.find_many(Sample.integer == 1)
        .exclude("float_num")
        .exclude("geo")
    )
    assert q._exclude_fields == ["float_num", "geo"]

    # Duplicates are not added
    q.exclude("float_num")
    assert q._exclude_fields == ["float_num", "geo"]


async def test_exclude_nonexistent_field(preset_documents):
    """Excluding a field that doesn't exist on the model is silently ignored."""
    result = (
        await Sample.find_many(Sample.integer == 0)
        .exclude("nonexistent_field")
        .to_list()
    )
    assert len(result) > 0
    for doc in result:
        assert isinstance(doc, Sample)
        assert doc.string == "test_0"


def test_exclude_projection_query():
    """Field references are stored as Python paths and only converted to
    MongoDB names when the query is built."""
    q = Sample.find_many().exclude(Sample.id, "float_num")
    assert q._exclude_fields == ["id", "float_num"]
    assert q._get_exclusion_projection() == {"_id": 0, "float_num": 0}

    # the MongoDB alias is accepted as input too, and normalises to the
    # same Python name rather than being added a second time
    assert Sample.find_many().exclude("_id")._exclude_fields == ["id"]

    # aliases are resolved per segment of a nested path
    nested = DocumentWithNestedAlias.find_many().exclude(
        "nested_field.unit_class"
    )
    assert nested._get_exclusion_projection() == {"nested_field.unitClass": 0}


def test_exclude_preserves_field_defaults():
    """The generated exclusion model must keep every non-excluded field
    exactly as declared.

    ``init_beanie`` installs ``ExpressionField`` class attributes on
    document models.  A naive ``create_model(__base__=...)`` makes
    Pydantic adopt those as field *defaults*, so every field would
    silently default to the string of its own name -- and that value
    would be written back to MongoDB on the next save.
    """
    exclusion_model = get_exclusion_model(Sample, ("float_num",))

    for name, field_info in get_model_fields(Sample).items():
        derived = get_model_fields(exclusion_model)[name]
        if name == "float_num":
            assert derived.default is None
            continue
        assert derived.default == field_info.default, name
        assert derived.default_factory is field_info.default_factory, name
        assert derived.alias == field_info.alias, name
        assert derived.is_required() == field_info.is_required(), name

    # revision_id is never stored unless use_revision is on, so it is the
    # field that surfaces the bug on every single excluded document.
    derived_fields = get_model_fields(exclusion_model)
    assert derived_fields["revision_id"].default is None
    assert derived_fields["id"].default is None
    assert derived_fields["const"].default == "TEST"


async def test_exclude_with_inheritance(preset_documents):
    """Exclusion applies to the concrete child class chosen by the
    ``_class_id`` dispatch, not to the class the query was issued on."""
    await Bicycle(color="red", frame=10, wheels=2).insert()

    children = (
        await Vehicle.find(Vehicle.color == "red", with_children=True)
        .exclude("frame")
        .to_list()
    )
    assert len(children) == 1
    assert isinstance(children[0], Bicycle)
    assert children[0].frame is None
    assert children[0].wheels == 2

    # querying the child directly keeps working
    direct = (
        await Bicycle.find(Bicycle.color == "red").exclude("wheels").to_list()
    )
    assert direct[0].wheels is None
    assert direct[0].frame == 10


async def test_exclude_with_union_doc():
    """A UnionDoc is not a Pydantic model; exclusion must still resolve
    against the registered document models."""
    await DocumentMultiModelOne(int_filed=1, shared=11).insert()

    docs = (
        await DocumentUnion.find(DocumentMultiModelOne.shared == 11)
        .exclude("int_filed")
        .to_list()
    )

    assert len(docs) == 1
    assert isinstance(docs[0], DocumentMultiModelOne)
    assert docs[0].int_filed is None
    assert docs[0].shared == 11


async def test_exclude_nested_path(preset_documents):
    """Dotted paths exclude a field inside an embedded model."""
    docs = (
        await Sample.find_many(Sample.integer == 0)
        .exclude(Sample.nested.integer)
        .to_list()
    )
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Sample)
        assert doc.nested.integer is None
        assert doc.nested.option_1 is not None
        assert doc.float_num is not None


def test_exclude_nested_path_unsupported_raises():
    """A nested path that cannot be rebuilt must fail loudly at
    .exclude() time rather than blow up during parsing."""
    with pytest.raises(ValueError, match=r"Cannot exclude nested field"):
        Sample.find_many().exclude("union.s")


async def test_exclude_with_aggregate_raises():
    """Exclusion is undefined for aggregation output, so combining the
    two must raise instead of being silently dropped."""
    with pytest.raises(
        ValueError, match=r"Cannot use exclude.*together with aggregate"
    ):
        Sample.find_many().exclude("float_num").aggregate([{"$count": "n"}])

    # the aggregation helpers route through aggregate() as well
    with pytest.raises(
        ValueError, match=r"Cannot use exclude.*together with aggregate"
    ):
        await Sample.find_many().exclude("float_num").sum(Sample.float_num)


def test_exclude_then_project_document_model_allowed():
    """project(document_model) is a no-op, so it must not be rejected -
    exclude() applies the same rule in the opposite order."""
    q = Sample.find_many(Sample.integer == 0).exclude("float_num")
    q.project(Sample)
    assert q._exclude_fields == ["float_num"]


async def test_exclude_refuses_whole_document_writes(preset_documents):
    """Excluded fields are None on the instance; writing the whole
    document back would overwrite the stored values."""
    doc = await Sample.find_one(Sample.integer == 0).exclude("float_num")
    assert doc.float_num is None

    for operation in ("save", "replace", "insert"):
        with pytest.raises(DocumentWasPartiallyLoaded):
            await getattr(doc, operation)()

    # targeted writes stay allowed
    await doc.set({Sample.string: "renamed"})
    reloaded = await Sample.get(doc.id)
    assert reloaded.string == "renamed"
    assert reloaded.float_num is not None


async def test_exclude_with_lazy_parse(preset_documents):
    """lazy_parse builds the document through a different branch of
    parse_obj, which must see the exclusion too."""
    docs = (
        await Sample.find_many(Sample.integer == 0, lazy_parse=True)
        .exclude("float_num")
        .to_list()
    )
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Sample)
        assert doc.string == "test_0"
        assert doc.float_num is None


async def test_exclude_is_part_of_the_cache_key(documents):
    """An excluded and a non-excluded query differ only in their
    projection, so the cache must not serve one for the other."""
    await documents(1, "cache_and_exclude")

    full = await DocumentTestModel.find(
        DocumentTestModel.test_str == "cache_and_exclude"
    ).to_list()
    assert full[0].test_int is not None

    excluded = (
        await DocumentTestModel.find(
            DocumentTestModel.test_str == "cache_and_exclude"
        )
        .exclude("test_int")
        .to_list()
    )
    assert excluded[0].test_int is None

    # ... and the cached full result is still intact afterwards
    again = await DocumentTestModel.find(
        DocumentTestModel.test_str == "cache_and_exclude"
    ).to_list()
    assert again[0].test_int is not None

    one_full = await DocumentTestModel.find_one(
        DocumentTestModel.test_str == "cache_and_exclude"
    )
    one_excluded = await DocumentTestModel.find_one(
        DocumentTestModel.test_str == "cache_and_exclude"
    ).exclude("test_int")
    assert one_full.test_int is not None
    assert one_excluded.test_int is None
