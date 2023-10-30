## Indexes setup

There are more than one way to set up indexes using Beanie

### Indexed function

To set up an index over a single field, the `Indexed` function can be used to wrap the type 
and does not require a `Settings` class:

```python
from beanie import Document, Indexed


class Sample(Document):
    num: Annotated[int, Indexed()]
    description: str
```

The `Indexed` function takes an optional `index_type` argument, which may be set to a pymongo index type:

```python
import pymongo

from beanie import Document, Indexed


class Sample(Document):
    description: Annotated[str, Indexed(index_type=pymongo.TEXT)]
```

The `Indexed` function also supports PyMongo's `IndexModel` kwargs arguments (see the [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel) for details). 
 
For example, to create a `unique` index:

```python
from beanie import Document, Indexed


class Sample(Document):
    name: Annotated[str, Indexed(unique=True)]
```

The `Indexed` function can also be used directly in the type annotation, by giving it the wrapped type as the first argument. Note that this might not work with some Pydantic V2 types, such as `UUID4` or `EmailStr`.

```python
from beanie import Document, Indexed


class Sample(Document):
    name: Indexed(str, unique=True)
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
