from beanie.odm.models import SortDirection
from tests.odm.query_builder.models import A


async def test_find_query():
    q = A.find_many(A.i == 1).find_parameters.get_filter_query()
    assert q == {"i": 1}

    q = A.find_many(A.i == 1, A.b.i >= 2).find_parameters.get_filter_query()
    assert q == {"$and": [{"i": 1}, {"b.i": {"$gte": 2}}]}

    q = (
        A.find_many(A.i == 1)
        .find_many(A.b.i >= 2)
        .find_parameters.get_filter_query()
    )
    assert q == {"$and": [{"i": 1}, {"b.i": {"$gte": 2}}]}


async def test_find_many(preset_documents):
    result = (
        await A.find_many(A.i > 1).find_many(A.b.o_d == None).to_list()
    )  # noqa
    assert len(result) == 3
    for a in result:
        assert a.i > 1
        assert a.b.o_d is None

    len_result = 0
    async for a in A.find_many(A.i > 1).find_many(A.b.o_d == None):  # noqa
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_skip(preset_documents):
    q = A.find_many(A.i > 1, skip=2)
    assert q.find_parameters.skip_number == 2

    q = A.find_many(A.i > 1).skip(2)
    assert q.find_parameters.skip_number == 2

    result = (
        await A.find_many(A.i > 1).find_many(A.b.o_d == None).skip(1).to_list()
    )  # noqa
    assert len(result) == 2
    for a in result:
        assert a.i > 1
        assert a.b.o_d is None

    len_result = 0
    async for a in A.find_many(A.i > 1).find_many(A.b.o_d == None).skip(
        1
    ):  # noqa
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_limit(preset_documents):
    q = A.find_many(A.i > 1, limit=2)
    assert q.find_parameters.limit_number == 2

    q = A.find_many(A.i > 1).limit(2)
    assert q.find_parameters.limit_number == 2

    result = (
        await A.find_many(A.i > 1)
        .find_many(A.b.o_d == None)
        .limit(2)
        .to_list()
    )  # noqa
    assert len(result) == 2
    for a in result:
        assert a.i > 1
        assert a.b.o_d is None

    len_result = 0
    async for a in A.find_many(A.i > 1).find_many(A.b.o_d == None).limit(
        2
    ):  # noqa
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_all(preset_documents):
    result = await A.find_all().to_list()
    assert len(result) == 10

    len_result = 0
    async for a in A.find_all():
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_one(preset_documents):
    a = await A.find_one(A.i > 1).find_one(A.b.o_d == None)  # noqa
    assert a.i > 1
    assert a.b.o_d is None

    a = await A.find_one(A.i > 100).find_one(A.b.o_d == None)  # noqa
    assert a is None


async def test_get(preset_documents):
    a = await A.find_one(A.i > 1).find_one(A.b.o_d == None)  # noqa
    assert a.i > 1
    assert a.b.o_d is None

    new_a = await A.get(a.id)
    assert new_a == a


async def test_sort(preset_documents):
    q = A.find_many(A.i > 1, sort="-i")
    assert q.find_parameters.sort_expressions == [
        ("i", SortDirection.DESCENDING)
    ]

    q = A.find_many(A.i > 1, sort="i")
    assert q.find_parameters.sort_expressions == [
        ("i", SortDirection.ASCENDING)
    ]

    q = A.find_many(A.i > 1).sort("-i")
    assert q.find_parameters.sort_expressions == [
        ("i", SortDirection.DESCENDING)
    ]

    q = A.find_many(A.i > 1).find_many(A.i < 100).sort("-i")
    assert q.find_parameters.sort_expressions == [
        ("i", SortDirection.DESCENDING)
    ]

    result = await A.find_many(A.i > 1, sort="-i").to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.i
        assert i_buf >= a.i
        i_buf = a.i

    result = await A.find_many(A.i > 1, sort="+i").to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.i
        assert i_buf <= a.i
        i_buf = a.i

    result = await A.find_many(A.i > 1, sort="i").to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.i
        assert i_buf <= a.i
        i_buf = a.i

    result = await A.find_many(A.i > 1, sort=-A.i).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.i
        assert i_buf >= a.i
        i_buf = a.i
