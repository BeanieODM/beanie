Beanie uses Motor as an async database engine. To init previously created documents, you should provide the Motor database instance and list of your document models to the `init_beanie(...)` function, as it is shown in the example:
```python
from beanie import init_beanie

class Sample(Document):
    name: str

# Crete Motor client
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb://user:pass@host:27017"
)

# Init beanie with the Product document class
await init_beanie(database=client.db_name, document_models=[Sample])
```

`init_beanie` supports not only list of classes for the document_models parameter, but also strings with the dot separated paths. Example:

```python
await init_beanie(
        database=db,
        document_models=[
            "app.models.DemoDocument",
        ],
    )
```