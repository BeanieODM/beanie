# Aggregations

[AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery) is used to aggregate data
over the whole collection or the subset selected with
the [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) query.

## Preset aggregations

[AggregateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods) is a list of preset
aggregations, which simplifies some use cases.

```python
class Sample(Document):
    category: str
    price: int
    count: int


sum_count = await Sample.find(Sample.price <= 100).sum(Sample.count)

# Or for the whole collection:

avg_price = await Sample.avg(Sample.count)

```

## Aggregate over collection

`AggregationQuery` implements async generator pattern - results
are available via `async for` loop

```python
class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int


async for item in Sample.aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}],
    aggregation_model=OutputItem,
):
    ...
```

or with `to_list` method:

```python
result = await Sample.aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}]
).to_list()
```

If the `aggregation_model` parameter is not set, it will return dicts.

## Over subsets

To aggregate over a specific subset, FindQuery could be used.

```python
result = await Sample.find(Sample.price < 10).aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$count"}}}]
).to_list()
```

