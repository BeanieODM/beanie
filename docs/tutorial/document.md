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

## Special Fields

As mentioned before, the `Document` class is inherited from the Pydantic `BaseModel` class. It uses all the same patterns of `BaseModel`. There are two places in which it differs however:

- There is alwas an `id` field present.
- Types can be declared to be `Indexed`. 

### The 'id' field

The `id` field of the `Document` class reflects the unique `_id` field of the MongoDB document. Each object of the `Document` type has this field, and it is always set if a document is present in the database. The default type of this field is `PydanticObjectId`.

```python
class Sample(Document):
    # the id field does not need to be declared explcitly
    num: int
    description: str

# query a single object from the database 
foo = await Sample.find_one(Sample.num > 5) 
print(foo.id)  # This will print the id
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

### Indexed

To setup an index over a single field the `Indexed` function can be used to wrap the type:

```python
from beanie import Indexed

class Sample(Document):
    num: Indexed(int)
    description: str
```

The `Indexed` function takes an optional argument `index_type`, which may be set to a pymongo index type:
```python
class Sample(Document):
    description: Indexed(str, index_type = pymongo.TEXT)
```

 The `Indexed` function also supports pymogo's `IndexModel` kwargs arguments (see the [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel) for details). 
 
For example to create `unique` index:

```python
class Sample(Document):
    name: Indexed(str, unique=True)
```

## Configuration of collections

Although the basic pydantic syntax allows you to set all aspects of individual fields, there is also some need to configure collections as a whole. In particular you might want to:

- Set the MongoDB collection name
- Configure multi-field indexes

This is done by defining a `Collection` class within your `Document` class.

### Declaring the collection name

To set MongoDB collection name you can use the `name` field of the `Collection` inner class.

```python
class Sample(Document):
    num: int
    description: str

    class Collection:
        name = "samples"
```

### Indexes

The `indexes` field of the inner `Collection` class is responsible for the indexes setup. It is a list where items could be:

- single key. Name of the document's field (this is equivalent to using the Indexed function described above without any additional arguments)
- list of (key, direction) pairs. Key - string, name of the document's field. Direction - pymongo direction (
  example: `pymongo.ASCENDING`)
- `pymongo.IndexModel` instance - the most flexible
  option. [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/beanie/api/pymongo/operations.html#pymongo.operations.IndexModel)

```python
class DocumentTestModelWithIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        indexes = [
            "test_int",
            [
                ("test_int", pymongo.ASCENDING),
                ("test_str", pymongo.DESCENDING),
            ],
            IndexModel(
                [("test_str", pymongo.DESCENDING)],
                name="test_string_index_DESCENDING",
            ),
        ]
```
