# Aggregations

You can aggregate and over the whole collection, using `aggregate()` method of the `Document` class, and over search criteria, using `FindMany` instance. 

#### Aggregation Methods

`FindMany` and `Document` classes implements [AggregateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods) interface with preset methods

Example of average calculation:

*With search criteria*
```python
avg_price = await Product.find(
    Product.category.name == "Chocolate"
).avg(Product.price)
```

*Over the whole collection*
```python
avg_price = await Product.avg(Product.price)
```

#### Native syntax

You can use the native PyMongo syntax of the aggregation pipelines to aggregate over the whole collection or over the subset too. `projection_model` parameter is responsible for the output format. It will return dictionaries, if this parameter is not provided.

```python
class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int


result = await Product.find(
    Product.category.name == "Chocolate").aggregate(
    [{"$group": {"_id": "$category.name", "total": {"$avg": "$price"}}}],
    projection_model=OutputItem
).to_list()

```