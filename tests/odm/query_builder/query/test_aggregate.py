from pydantic import Field
from pydantic.main import BaseModel

from tests.odm.query_builder.models import Sample


async def test_aggregate(preset_documents):
    result = await Sample.aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    ).to_list()
    assert len(result) == 4
    assert {"_id": "test_3", "total": 3} in result
    assert {"_id": "test_1", "total": 3} in result
    assert {"_id": "test_0", "total": 0} in result
    assert {"_id": "test_2", "total": 6} in result


async def test_aggregate_with_filter(preset_documents):
    result = (
        await Sample.find(Sample.increment >= 4)
        .aggregate(
            [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
        )
        .to_list()
    )
    assert len(result) == 3
    assert {"_id": "test_1", "total": 2} in result
    assert {"_id": "test_2", "total": 6} in result
    assert {"_id": "test_3", "total": 3} in result


async def test_aggregate_with_projection_model(preset_documents):
    class OutputItem(BaseModel):
        id: str = Field(None, alias="_id")
        total: int

    ids = []
    async for i in Sample.find(Sample.increment >= 4).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}],
        projection_model=OutputItem,
    ):
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
