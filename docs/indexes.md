## Single field indexes

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
 The `Indexed` function supports pymogo `IndexModel` kwargs arguments ([PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel)). 
 
For example to create `unique` index:

```python
class Sample(Document):
    name: Indexed(str, unique=True)
```

## Complex indexes
More complex indexes can be set up by the `indexes` field in a Collection class. It is a list where items could be:

- single key. Name of the document's field (this is equivalent to using the Indexed function described above)
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

Complex and simple indices can be used in tandem.