import pytest
from pydantic import Field
from pydantic.main import BaseModel

from tests.odm.models import Sample


async def test_aggregate(preset_documents):
    q = Sample.aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    assert q.get_aggregation_pipeline() == [
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}
    ]
    result = await q.to_list()
    assert len(result) == 4
    assert {"_id": "test_3", "total": 3} in result
    assert {"_id": "test_1", "total": 3} in result
    assert {"_id": "test_0", "total": 0} in result
    assert {"_id": "test_2", "total": 6} in result


async def test_aggregate_with_filter(preset_documents):
    q = Sample.find(Sample.increment >= 4).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    assert q.get_aggregation_pipeline() == [
        {"$match": {"increment": {"$gte": 4}}},
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
    ]
    result = await q.to_list()
    assert len(result) == 3
    assert {"_id": "test_1", "total": 2} in result
    assert {"_id": "test_2", "total": 6} in result
    assert {"_id": "test_3", "total": 3} in result


async def test_aggregate_with_projection_model(preset_documents):
    class OutputItem(BaseModel):
        id: str = Field(None, alias="_id")
        total: int

    ids = []
    q = Sample.find(Sample.increment >= 4).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}],
        projection_model=OutputItem,
    )
    assert q.get_aggregation_pipeline() == [
        {"$match": {"increment": {"$gte": 4}}},
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
        {"$project": {"_id": 1, "total": 1}},
    ]
    async for i in q:
        if i.id == "test_1":
            assert i.total == 2
        elif i.id == "test_2":
            assert i.total == 6
        elif i.id == "test_3":
            assert i.total == 3
        else:
            raise KeyError
        ids.append(i.id)
    assert set(ids) == {"test_1", "test_2", "test_3"}


async def test_aggregate_with_session(preset_documents, session):
    q = Sample.find(Sample.increment >= 4).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}],
        session=session,
    )
    assert q.session == session

    q = Sample.find(Sample.increment >= 4, session=session).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    assert q.session == session

    result = await q.to_list()

    assert len(result) == 3
    assert {"_id": "test_1", "total": 2} in result
    assert {"_id": "test_2", "total": 6} in result
    assert {"_id": "test_3", "total": 3} in result


async def test_aggregate_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        await Sample.find(Sample.increment >= 4).aggregate(
            [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}],
            wrong=True,
        )

    with pytest.raises(TypeError):
        await Sample.find(Sample.increment >= 4).aggregate(
            [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}],
            hint="integer_1",
        )


async def test_clone(preset_documents):
    q = Sample.find(Sample.increment >= 4).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    new_q = q.clone()
    new_q.aggregation_pipeline.append({"a": "b"})
    assert q.get_aggregation_pipeline() == [
        {"$match": {"increment": {"$gte": 4}}},
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
    ]
    assert new_q.get_aggregation_pipeline() == [
        {"$match": {"increment": {"$gte": 4}}},
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
        {"a": "b"},
    ]
