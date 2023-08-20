# Defining a document

The `Document` class in Beanie is responsible for mapping and handling the data
from the collection. It is inherited from the `BaseModel` Pydantic class, so it
follows the same data typing and parsing behavior.

```python
from typing import Optional

import pymongo
from pydantic import BaseModel

from beanie import Document, Indexed


class Category(BaseModel):
    name: str
    description: str


class Product(Document):  # This is the model
    name: str
    description: Optional[str] = None
    price: Indexed(float, pymongo.DESCENDING)
    category: Category

    class Settings:
        name = "products"
        indexes = [
            [
                ("name", pymongo.TEXT),
                ("description", pymongo.TEXT),
            ],
        ]

```

## Fields

As it was mentioned before, the `Document` class is inherited from the Pydantic `BaseModel` class. 
It uses all the same patterns of `BaseModel`. But also it has special types of fields:

- id
- Indexed

### id

`id` field of the `Document` class reflects the unique `_id` field of the MongoDB document. 
Each object of the `Document` type has this field. 
The default type of this is [PydanticObjectId](../api-documentation/fields.md/#pydanticobjectid).

```python
class Sample(Document):
    num: int
    description: str

foo = await Sample.find_one(Sample.num > 5)

print(foo.id)  # This will print id

bar = await Sample.get(foo.id)  # get by id
```

If you prefer another type, you can set it up too. For example, UUID:

```python
from uuid import UUID, uuid4

from pydantic import Field


class Sample(Document):
    id: UUID = Field(default_factory=uuid4)
    num: int
    description: str
```

### Indexed

To set up an index over a single field, the `Indexed` function can be used to wrap the type:

```python
from beanie import Indexed


class Sample(Document):
    num: Indexed(int)
    description: str
```

The `Indexed` function takes an optional argument `index_type`, which may be set to a pymongo index type:

```python
class Sample(Document):
    description: Indexed(str, index_type=pymongo.TEXT)
```

The `Indexed` function also supports pymongo `IndexModel` kwargs arguments ([PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel)). 
 
For example, to create a `unique` index:

```python
class Sample(Document):
    name: Indexed(str, unique=True)
```

## Settings

The inner class `Settings` is used to configure:

- MongoDB collection name
- Indexes
- Encoders
- Use of `revision_id`
- Use of cache
- Use of state management
- Validation on save
- Configure if nulls should be saved to the database

### Collection name

To set MongoDB collection name, you can use the `name` field of the `Settings` inner class.

```python
class Sample(Document):
    num: int
    description: str

    class Settings:
        name = "samples"
```

### Indexes

The `indexes` field of the inner `Settings` class is responsible for the indexes' setup. 
It is a list where items can be:

- Single key. Name of the document's field (this is equivalent to using the Indexed function described above)
- List of (key, direction) pairs. Key - string, name of the document's field. Direction - pymongo direction (
  example: `pymongo.ASCENDING`)
- `pymongo.IndexModel` instance - the most flexible
  option. [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel)

```python
class DocumentTestModelWithIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Settings:
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

### Encoders

The `bson_encoders` field of the inner `Settings` class defines how the Python types are going to be represented 
when saved in the database. The default conversions can be overridden with this.

The `ip` field in the following example is converted to String by default:

```python
from ipaddress import IPv4Address


class Sample(Document):
    ip: IPv4Address
```
> **Note:** Default conversions are defined in `beanie.odm.utils.bson.ENCODERS_BY_TYPE`.

However, if you want the `ip` field to be represented as Integer in the database, 
you need to override the default encoders like this:

```python
from ipaddress import IPv4Address


class Sample(Document):
    ip: IPv4Address

    class Settings:
        bson_encoders = {
          IPv4Address: int
        }
```

You can also define your own function for the encoding:

```python
from ipaddress import IPv4Address


def ipv4address_to_int(v: IPv4Address):
    return int(v)

class Sample(Document):
    ip: IPv4Address

    class Settings:
        bson_encoders = {
          IPv4Address: ipv4address_to_int
        }
```

### Keep nulls

By default, Beanie saves fields with `None` value as `null` in the database.

But if you don't want to save `null` values, you can set `keep_nulls` to `False` in the `Settings` class:

```python
class Sample(Document):
    num: int
    description: Optional[str] = None

    class Settings:
        keep_nulls = False
```

