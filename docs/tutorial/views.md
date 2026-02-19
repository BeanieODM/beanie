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
from pymongo import AsyncMongoClient

from beanie import init_beanie


async def main():
    uri = "mongodb://beanie:beanie@localhost:27017"
    client = AsyncMongoClient(uri)
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

## Views with linked documents

Views can include `Link` fields just like regular documents. Use `fetch_links=True` in
find operations to resolve linked documents via `$lookup` aggregation:

```python
from beanie import Document, Link, View


class Author(Document):
    name: str


class BookView(View):
    title: str
    author: Link[Author]

    class Settings:
        source = Book
        pipeline = [
            {"$project": {"title": 1, "author": 1}},
        ]


# Find with automatic link resolution
books = await BookView.find(
    BookView.title == "Beanie Guide",
    fetch_links=True,
).to_list()

# author is now a full Author document, not a DBRef
print(books[0].author.name)
```

You can also fetch links on demand for an individual view instance:

```python
book = await BookView.find_one(BookView.title == "Beanie Guide")
await book.fetch_all_links()
print(book.author.name)
```
