## Indexes setup

There are more than one way to set up indexes using Beanie

### Indexed function

To set up an index over a single field, the `Indexed` function can be used to wrap the type 
and does not require a `Settings` class:

```python
from beanie import Document, Indexed


class Sample(Document):
    num: Indexed(int)
    description: str
```

The `Indexed` function takes an optional `index_type` argument, which may be set to a pymongo index type:

```python
import pymongo

from beanie import Document, Indexed


class Sample(Document):
    description: Indexed(str, index_type=pymongo.TEXT)
```

The `Indexed` function also supports PyMongo's `IndexModel` kwargs arguments (see the [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel) for details). 
 
For example, to create a `sparse` index:

```python
from beanie import Document, Indexed


class Sample(Document):
    name: Indexed(str, sparse=True)
```

### Multi-field indexes

The `indexes` field of the inner `Settings` class is responsible for more complex indexes. 
It is a list where items can be:

- Single key. Name of the document's field (this is equivalent to using the Indexed function described above without any additional arguments)
- List of (key, direction) pairs. Key - string, name of the document's field. Direction - pymongo direction (
  example: `pymongo.ASCENDING`)
- `pymongo.IndexModel` instance - the most flexible
  option. [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel)

```python
import pymongo
from pymongo import IndexModel

from beanie import Document


class Sample(Document):
    test_int: int
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

### Unique indexes
Unique indexes can be specified in different ways:
1) By specifying `unique=True` kwarg either in `Indexed` function or IndexModel definition inside `Settings` inner class.
2) By using `Unique` function which is a wrapper of `Indexed` one with predefined `unique=True` kwarg.

```python
from beanie import Document, Indexed, Unique


class Sample(Document):
    name: Unique(str)
    title: Indexed(str)
```

Beanie can also handle unique indexes for `Optional` fields, despite this being really tricky in mongoDB.

```python
from typing import Optional
from beanie import Document, Indexed, Unique


class Sample(Document):
    name: Unique(str)
    title: Indexed(str)
    tag: Unique(Optional[str])
```

In python 3.11+ it can be declared like `tag: Unique(str) | None`.

As well as using corresponding pydantic `Field` param: `tag: str = Field(allow_none=True)`.
