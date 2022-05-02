# Multi-model mode

A Document can be used in multi-model mode. If two or more Document classes have the same collection name in the Settings and multi-model mode turned on, they will save documents into the same collection, but read operations for each Document class will happen separately. One model will not find documents of another model.

## Example

Create documents with multi-model mode turned on

```python
from beanie import Document


class One(Document):
    int_filed: int = 0
    shared: int = 0        

    class Settings:
        name = "multi_model"  # set collection name
        multi_model = True    # turn on multi-model mode


class Two(Document):
    str_filed: str = "test"
    shared: int = 0

    class Settings:
        name = "multi_model"  # set collection name
        multi_model = True    # turn on multi-model mode
```

The schemas could be incompatible.

Insert a document

```python
await One().insert()
await One().insert()
await One().insert()
```

Find all the doc of the first type:

```python
docs = await One.all().to_list()
print(len(docs))

>> 3
```

Of the second type:

```python
docs = await Two.all().to_list()
print(len(docs))

>> 0
```

Aggregations will work separately for these two document classes too.