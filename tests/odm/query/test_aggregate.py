import pytest
from pydantic import Field
from pydantic.main import BaseModel
from pymongo.errors import OperationFailure

from beanie.odm.enums import SortDirection
from beanie.odm.utils.find import construct_lookup_queries
from tests.odm.models import DocumentWithTextIndexAndLink, Sample


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


async def test_aggregate_with_sort_skip(preset_documents):
    q = Sample.find(sort="_id", skip=2).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    assert q.get_aggregation_pipeline() == [
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
        {"$sort": {"_id": SortDirection.ASCENDING}},
        {"$skip": 2},
    ]
    assert await q.to_list() == [
        {"_id": "test_2", "total": 6},
        {"_id": "test_3", "total": 3},
    ]


async def test_aggregate_with_sort_limit(preset_documents):
    q = Sample.find(sort="_id", limit=2).aggregate(
        [{"$group": {"_id": "$string", "total": {"$sum": "$integer"}}}]
    )
    assert q.get_aggregation_pipeline() == [
        {"$group": {"_id": "$string", "total": {"$sum": "$integer"}}},
        {"$sort": {"_id": SortDirection.ASCENDING}},
        {"$limit": 2},
    ]
    assert await q.to_list() == [
        {"_id": "test_0", "total": 0},
        {"_id": "test_1", "total": 3},
    ]


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
    with pytest.raises(OperationFailure):
        await (
            Sample.find(Sample.increment >= 4)
            .aggregate(
                [
                    {
                        "$group": {
                            "_id": "$string",
                            "total": {"$sum": "$integer"},
                        }
                    }
                ],
                wrong=True,
            )
            .to_list()
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


@pytest.mark.parametrize("text_query_count", [0, 1, 2])
@pytest.mark.parametrize("non_text_query_count", [0, 1, 2])
async def test_with_text_queries(
    text_query_count: int, non_text_query_count: int
):
    text_query = {"$text": {"$search": "text_search"}}
    non_text_query = {"s": "test_string"}
    aggregation_pipeline = [{"$count": "count"}]
    queries = []

    if text_query_count:
        queries.append(text_query)
        if text_query_count > 1:
            queries.append(text_query)

    if non_text_query_count:
        queries.append(non_text_query)
        if non_text_query_count > 1:
            queries.append(non_text_query)

    query = DocumentWithTextIndexAndLink.find(*queries, fetch_links=True)

    expected_aggregation_pipeline = []
    if text_query_count:
        expected_aggregation_pipeline.append(
            {"$match": text_query}
            if text_query_count == 1
            else {"$match": {"$and": [text_query, text_query]}}
        )

    expected_aggregation_pipeline.extend(
        construct_lookup_queries(query.document_model)
    )

    if non_text_query_count:
        expected_aggregation_pipeline.append(
            {"$match": non_text_query}
            if non_text_query_count == 1
            else {"$match": {"$and": [non_text_query, non_text_query]}}
        )

    expected_aggregation_pipeline.extend(aggregation_pipeline)

    assert (
        query.build_aggregation_pipeline(*aggregation_pipeline)
        == expected_aggregation_pipeline
    )
