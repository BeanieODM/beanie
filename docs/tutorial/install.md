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
from typing import Optional
from pydantic import BaseModel
from beanie import Document


class Category(BaseModel):
    name: str
    description: str


class Product(Document):  # This is the model
    name: str
    description: Optional[str] = None
    price: float
    category: Category

    class Collection:
        name = "products"

```

TODO - put here info about clas Collection

## Init

text abut motor client and db

```python
async def init():
    # Crete Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )

    # Init beanie with the Note document class
    await init_beanie(database=client.db_name, document_models=[Product])
```

