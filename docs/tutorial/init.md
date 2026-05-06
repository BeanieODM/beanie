Beanie uses Async PyMongo as an async database engine. 
To initialize previously created documents, you should provide an Async PyMongo database instance 
and a list of your document models to the `init_beanie(...)` function, as it is shown in the example:

```python
from beanie import init_beanie, Document
from pymongo import AsyncMongoClient

class Sample(Document):
    name: str

async def init():
    # Create Async PyMongo client
    client = AsyncMongoClient(
        "mongodb://user:pass@host:27017"
    )

    # Initialize beanie with the Sample document class and a database
    await init_beanie(database=client.db_name, document_models=[Sample])
```

This creates the collection (if necessary) and sets up any indexes that are defined.

### Async PyMongo vs Motor

Beanie 2.x uses PyMongo's async driver under the hood. If you are
upgrading an older project that initialized Beanie with a Motor database
instance, replace it with `pymongo.AsyncMongoClient` as shown above.

Passing a Motor database to `init_beanie(...)` can lead to initialization
errors such as `TypeError: MotorDatabase object is not callable`, because
the database object does not expose the same async PyMongo client API that
Beanie expects.


`init_beanie` supports not only a list of classes as the document_models argument, 
but also strings with dot-separated paths:

```python
await init_beanie(
        database=client.db_name,
        document_models=[
            "app.models.DemoDocument",
        ],
    )
```

### Warning

`init_beanie` supports the parameter named `allow_index_dropping` that will drop indexes from your collections. 
`allow_index_dropping` is by default set to `False`. If you set this to `True`, 
ensure that you are not managing your indexes in another manner. 
If you are, these will be deleted when setting `allow_index_dropping=True`.
