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
Each document by default has `id` ObjectId field, which reflects `_id` MongoDB document field. It can be used later as an argument for the `get()` method.

To set up the collection name it uses inner class Collection.

To set up a simple index [Indexed](/beanie/api/fields/#indexed) function over the data type can be used

For the complex cases indexes should be set up in the Collection inner class also.

More information about indexes could be found [here](/beanie/tutorial/indexes/)

## Init

Beanie uses Motor as a driver.

```python
from beanie import init_beanie

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

