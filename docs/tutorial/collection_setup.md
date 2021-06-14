# Indexes & collection names

Although the basic pydantic syntax allows you to set all aspects of individual fields, there is also some need to configure collections as a whole. In particular you might want to:

- Set the MongoDB collection name
- Configure indexes

This is done by defining a `Collection` class within your `Document` class.

## Declaring the collection name

To set MongoDB collection name you can use the `name` field of the `Collection` inner class.

```python
class Sample(Document):
    num: int
    description: str

    class Collection:
        name = "samples"
```

## Indexes

### Indexed function

To setup an index over a single field the `Indexed` function can be used to wrap the type and does not require a `Collection` class:

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

### Multi-field indices

The `indexes` field of the inner `Collection` class is responsible for more complex indexes. It is a list where items could be:

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
