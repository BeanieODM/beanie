# Aggregations

You can perform aggregation queries through beanie as well. For example, to calculate the average:

```python
# With a search:
avg_price = await Product.find(
    Product.category.name == "Chocolate"
).avg(Product.price)

# Over the whole collection:
avg_price = await Product.avg(Product.price)
```

A full list of available methods can be found [here](/api-documentation/interfaces/#aggregatemethods).

You can also use the native PyMongo syntax by calling the `aggregate` method. 
However, as Beanie will not know what output to expect, you will have to supply a projection model yourself. 
If you do not supply a projection model, then a dictionary will be returned.

```python
class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: float


result = await Product.find(
    Product.category.name == "Chocolate").aggregate(
    [{"$group": {"_id": "$category.name", "total": {"$avg": "$price"}}}],
    projection_model=OutputItem
).to_list()

```
