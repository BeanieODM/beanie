Beanie uses Motor as an async database engine. To init previously created documents, you should provide a Motor database instance and list of your document models to the `init_beanie(...)` function, as it is shown in the example:
```python
from beanie import init_beanie, Document
import motor.motor_asyncio

class Sample(Document):
    name: str

async def init():
    # Crete Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )

    # Init beanie with the Product document class and a database
    await init_beanie(database=client.db_name, document_models=[Sample])
```

This creates the collection (if needed) and sets up any indexes that are defined.


`init_beanie` supports not only list of classes for the document_models parameter, but also strings with the dot separated paths:

```python
await init_beanie(
        database=db,
        document_models=[
            "app.models.DemoDocument",
        ],
    )
```

### Warning
`init_beanie` supports a parameter `allow_index_dropping` this will drop indexes from your collection(s).  `allow_index_dropping` is default set to `False` if you set this to `True` your indexes will get dropped, ensure that you are not managing your indexes in another manner, if you are these will be deleted when setting `allow_index_dropping = True`