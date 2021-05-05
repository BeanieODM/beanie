## Installation

### PIP

```shell
pip install beanie
```

### Poetry

```shell
poetry add beanie
```

## Document set up

```python
import pymongo
from typing import Optional

from pydantic import BaseModel

from beanie import Document
from beanie import Indexed


class Category(BaseModel):
    name: str
    description: str


class Product(Document):  # This is the model
    name: str
    description: Optional[str] = None
    price: Indexed(float, pymongo.DESCENDING)
    category: Category

    class Collection:
        name = "products"
        indexes = [
            [
                ("name", pymongo.TEXT),
                ("description", pymongo.TEXT),
            ],
        ]

```

To set up collection name it uses inner class Collection.

To set up simple index [Indexed](/api/fields/#indexed) function over the data type can be used

For the complex cases indexes should be set up in the Collection inner class also.

## Init

Beanie uses motor as a driver. 

```python
# Crete Motor client
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb://user:pass@host:27017"
)

# Init beanie with the Product document class
await init_beanie(database=client.db_name, document_models=[Product])
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

