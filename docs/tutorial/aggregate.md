# Aggregations

[AggregationQuery](/api/queries/#aggregationquery) is used to aggregate data
over the whole collection or the subset selected
with the [FindMany](/api/queries/#findmany) query.

## Preset aggregations

[AggregateMethods](/api/interfaces/#aggregatemethods) is a list of preset
aggregations, which simplifies some use cases.

```python
class Sample(Document):
    category: str
    price: int
    count: int


sum_count = await Document.find(Sample.price <= 100).sum(Sample.count)

# Or for the whole collection:

sum_count = await Document.sum(Sample.count)

```

## Aggregate over collection

As FindMany query it implements async generator pattern - aggregation result
are available via async loop

```python
    class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int


async for i in Sample.aggregate(
        [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}],
        aggregation_model=OutputItem,
):
    ...
```

or with `to_list` method:

```python
result = await Sample.aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}]
)
```

If the `aggregation_model` parameter is not set, it will return dicts.

## Over subsets

To aggregate over a specific subset, FindQuery could be used.

```python
result = await Sample.fin(Sample.price< 10).aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}]
)
```

