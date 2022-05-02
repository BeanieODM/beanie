# Collection setup (name, indexes, timeseries)

Although the basic pydantic syntax allows you to set all aspects of individual fields, there is also some need to configure collections as a whole. In particular you might want to:

- Set the MongoDB collection name
- Configure indexes

This is done by defining a `Settings` class within your `Document` class.

## Declaring the collection name

To set MongoDB collection name you can use the `name` field of the `Settings` inner class.

```python
from beanie import Document


class Sample(Document):
    num: int
    description: str

    class Settings:
        name = "samples"
```

## Indexes

### Indexed function

To setup an index over a single field the `Indexed` function can be used to wrap the type and does not require a `Settings` class:

```python
from beanie import Document, Indexed


class Sample(Document):
    num: Indexed(int)
    description: str
```

The `Indexed` function takes an optional argument `index_type`, which may be set to a pymongo index type:
```python
import pymongo

from beanie import Document, Indexed


class Sample(Document):
    description: Indexed(str, index_type = pymongo.TEXT)
```

 The `Indexed` function also supports pymogo's `IndexModel` kwargs arguments (see the [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel) for details). 
 
For example to create `unique` index:

```python
from beanie import Document, Indexed


class Sample(Document):
    name: Indexed(str, unique=True)
```

### Multi-field indices

The `indexes` field of the inner `Settings` class is responsible for more complex indexes. It is a list where items could be:

- single key. Name of the document's field (this is equivalent to using the Indexed function described above without any additional arguments)
- list of (key, direction) pairs. Key - string, name of the document's field. Direction - pymongo direction (
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

## Time series

You can setup a timeseries collection using inner class `Settings`.

**Be aware, timeseries collections a supported by MongoDB 5.0 and higher only.**

```python
from datetime import datetime

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field


class Sample(Document):
    ts: datetime = Field(default_factory=datetime.now)
    meta: str

    class Settings:
        timeseries = TimeSeriesConfig(
            time_field="ts", #  Required
            meta_field="meta", #  Optional
            granularity=Granularity.hours, #  Optional
            expire_after_seconds=2  #  Optional
        )
```

TimeSeriesConfig fields are reflecting the respective parameters of the timeseries creation function of MongoDB.

MongoDB documentation: https://docs.mongodb.com/manual/core/timeseries-collections/