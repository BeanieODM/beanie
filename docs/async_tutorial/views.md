# Views

Virtual views are aggregation pipelines stored in MongoDB that act as collections for reading operations.
You can use the `View` class the same way as `Document` for `find` and `aggregate` operations.

## Here are some examples.

Create a view:

```python
from pydantic import Field

from beanie import Document, View


class Bike(Document):
    type: str
    frame_size: int
    is_new: bool


class Metrics(View):
    type: str = Field(alias="_id")
    number: int
    new: int

    class Settings:
        source = Bike
        pipeline = [
            {
                "$group": {
                    "_id": "$type",
                    "number": {"$sum": 1},
                    "new": {"$sum": {"$cond": ["$is_new", 1, 0]}}
                }
            },
        ]

```

Initialize Beanie:

```python
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie


async def main():
    uri = "mongodb://beanie:beanie@localhost:27017"
    client = AsyncIOMotorClient(uri)
    db = client.bikes

    await init_beanie(
        database=db, 
        document_models=[Bike, Metrics],
        recreate_views=True,
    )
```

Create bikes:

```python
await Bike(type="Mountain", frame_size=54, is_new=True).insert()
await Bike(type="Mountain", frame_size=60, is_new=False).insert()
await Bike(type="Road", frame_size=52, is_new=True).insert()
await Bike(type="Road", frame_size=54, is_new=True).insert()
await Bike(type="Road", frame_size=58, is_new=False).insert()
```

Find metrics for `type == "Road"`

```python
results = await Metrics.find(Metrics.type == "Road").to_list()
print(results)

>> [Metrics(type='Road', number=3, new=2)]
```

Aggregate over metrics to get the count of all the new bikes:

```python
results = await Metrics.aggregate([{
    "$group": {
        "_id": None,
        "new_total": {"$sum": "$new"}
    }
}]).to_list()

print(results)

>> [{'_id': None, 'new_total': 3}]
```

A better result can be achieved by using find query aggregation syntactic sugar:

```python
results = await Metrics.all().sum(Metrics.new)

print(results)

>> 3
```
