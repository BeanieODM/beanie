# Defining a document
The `Document` class in Beanie is responsible for mapping and handling the data
from the collection. It is inherited from the `BaseModel` Pydantic class, so it
follows the same data typing and parsing behavior.

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

## The 'id' field

Each `Document` has a `id` field. The `id` field  reflects the unique `_id` field of the MongoDB document. Each object of the `Document` type has this field, and it is always set if a document is present in the database. The default type of this field is `PydanticObjectId`.

```python
class Sample(Document):
    # the id field does not need to be declared explcitly
    num: int
    description: str

# query a single object from the database 
foo = await Sample.find_one(Sample.num > 5) 
print(foo.id)  # This will print the id

```

You can reference other objects using their id, for example if you want to list Sample ids:

```python
class ReferencesSample(Document):
    name : str
    mysamples : List[PydanticObjectId]
```

If you prefer another type, then you can overide the default. For example, to set it to UUID:

```python
from pydantic import Field
from uuid import UUID, uuid4

class Sample(Document):
    id: UUID = Field(default_factory=uuid4)
    num: int
    description: str
```
