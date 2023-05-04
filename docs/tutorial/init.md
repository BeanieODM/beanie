Beanie leverages Motor as an asynchronous database engine. To initialize your pre-existing documents, you must provide a Motor database instance and a list of your document models to the `init_beanie(...)` function, as demonstrated in the following example:

```python
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient

class Sample(Document):
    name: str

async def init():
    # Create Motor client
    client = AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )

    # Initialize beanie with the Product document class and a database
    await init_beanie(database=client.db_name, document_models=[Sample])
```

This will create the collection (if needed) and set up any defined indexes.

The `init_beanie` function also accepts strings with dot-separated paths for the `document_models` argument:

```python
await init_beanie(
        database=client.db_name,
        document_models=[
            "app.models.DemoDocument",
        ],
    )
```

### Warning

`init_beanie` includes an optional parameter called `allow_index_dropping`, which, if enabled, will drop indexes from your collections. By default, `allow_index_dropping` is set to `False`. If you decide to set it to `True`, ensure that you are not managing your indexes in any other way. If you are, these indexes will be deleted when `allow_index_dropping=True`.