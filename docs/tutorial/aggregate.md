# Aggregations

## Built-in Aggregation Methods

Beanie exposes the most common aggregation operations as chainable query
methods.  They can be applied to the whole collection or scoped to a filtered
subset of documents.

```python
from beanie import Document
from pydantic import Field


class Product(Document):
    name: str
    price: float
    category: str
    in_stock: bool = True

    class Settings:
        name = "products"
```

### Average

```python
# Average price across the whole collection
avg_price = await Product.avg(Product.price)

# Average price within a category
avg_chocolate_price = await Product.find(
    Product.category == "Chocolate"
).avg(Product.price)
```

### Sum

```python
total_value = await Product.sum(Product.price)

total_chocolate_value = await Product.find(
    Product.category == "Chocolate"
).sum(Product.price)
```

### Min and Max

```python
cheapest = await Product.min(Product.price)
most_expensive = await Product.max(Product.price)
```

### Count

```python
total_products = await Product.count()
chocolate_count = await Product.find(Product.category == "Chocolate").count()
```

A full list of available methods is in the
[API documentation](../api-documentation/interfaces.md/#aggregatemethods).

---

## Native Aggregation Pipelines

For more complex queries, use `aggregate()` with a standard MongoDB pipeline.
Because Beanie cannot infer the output shape, you must provide a
`projection_model` (a Pydantic `BaseModel`) or accept plain `dict` results.

### Group by field and compute average

```python
from pydantic import BaseModel


class CategoryStats(BaseModel):
    id: str = Field(alias="_id")
    average_price: float
    total_products: int


stats = await Product.aggregate(
    [
        {
            "$group": {
                "_id": "$category",
                "average_price": {"$avg": "$price"},
                "total_products": {"$sum": 1},
            }
        },
        {"$sort": {"average_price": -1}},
    ],
    projection_model=CategoryStats,
).to_list()

for s in stats:
    print(f"{s.id}: avg={s.average_price:.2f}, count={s.total_products}")
```

### Filter then aggregate

```python
class PriceBucket(BaseModel):
    id: str = Field(alias="_id")
    count: int


buckets = await Product.find(Product.in_stock == True).aggregate(
    [
        {
            "$bucket": {
                "groupBy": "$price",
                "boundaries": [0, 10, 50, 100, 500],
                "default": "500+",
                "output": {"count": {"$sum": 1}},
            }
        }
    ],
    projection_model=PriceBucket,
).to_list()
```

### Without a projection model (returns dicts)

```python
raw_results = await Product.aggregate(
    [{"$group": {"_id": "$category", "total": {"$sum": "$price"}}}]
).to_list()

for row in raw_results:
    print(row["_id"], row["total"])
```

---

## Aggregation vs. Find

| Scenario | Recommended approach |
|---|---|
| Simple filtering and sorting | `find()` + `sort()` / `skip()` / `limit()` |
| Single-metric statistics (avg, sum, min, max) | Built-in aggregation methods |
| Grouping, bucketing, reshaping documents | `aggregate()` with a pipeline |
| Joining collections (`$lookup`) | `aggregate()` with a pipeline |
| Complex multi-stage transformations | `aggregate()` with a pipeline |

---

## Tips

- **Use `$match` early** in the pipeline to reduce the working set before
  expensive stages like `$group` or `$lookup`.
- **Leverage indexes** — a `$match` on an indexed field will use that index
  even inside an aggregation pipeline.
- **Reuse find filters** — `Product.find(Product.in_stock == True).aggregate(...)`
  prepends a `$match` stage automatically, so you do not need to repeat the
  filter inside the pipeline.
