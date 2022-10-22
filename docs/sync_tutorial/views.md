# Views

Virtual views are aggregation pipelines, stored in MongoDB, that act as collections for reading operations.
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
from pymongo import MongoClient
from beanie import init_beanie_sync


def main():
    uri = "mongodb://beanie:beanie@localhost:27017"
    client = MongoClient(uri)
    db = client.bikes

    init_beanie_sync(
        database=db, 
        document_models=[Bike, Metrics],
        recreate_views=True,
    )
```

Create bikes:

```python
Bike(type="Mountain", frame_size=54, is_new=True).insert()
Bike(type="Mountain", frame_size=60, is_new=False).insert()
Bike(type="Road", frame_size=52, is_new=True).insert()
Bike(type="Road", frame_size=54, is_new=True).insert()
Bike(type="Road", frame_size=58, is_new=False).insert()
```

Find metrics for `type == "Road"`

```python
results = Metrics.find(Metrics.type == "Road").to_list()
print(results)

>> [Metrics(type='Road', number=3, new=2)]
```

Aggregate over metrics to get the number of all the new bikes:

```python
results = Metrics.aggregate([{
    "$group": {
        "_id": None,
        "new_total": {"$sum": "$new"}
    }
}]).to_list()

print(results)

>> [{'_id': None, 'new_total': 3}]
```

A better result could be reached using find query aggregation syntax sugar:

```python
results = Metrics.all().sum(Metrics.new)

print(results)

>> 3
```
