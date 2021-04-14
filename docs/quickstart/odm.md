

## Init

```python
import asyncio
from typing import List

import motor
from beanie import Document
from beanie import init_beanie
from pydantic import BaseModel


# CREATE BEANIE DOCUMENT STRUCTURE

class SubDocument(BaseModel):
    test_str: str


class DocumentTestModel(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str


async def main():
    # CREATE MOTOR CLIENT AND DB

    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017/db",
        serverSelectionTimeoutMS=100
    )
    db = client.beanie_db

    # INIT BEANIE

    await init_beanie(database=db, document_models=[DocumentTestModel])


asyncio.run(main())
```

`init_beanie` supports not only list of classes for the document_models parameter, but also strings with the dot separated paths. Example:

```python
await init_beanie(
        database=db,
        document_models=[
            "app.models.DemoDocument",
        ],
    )
```

## Create

### Create a document (insert it)

```python
document = DocumentTestModel(
    test_int=42,
    test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
    test_str="kipasa",
)

await document.create()
```

### Insert one document

```python
document = DocumentTestModel(
    test_int=42,
    test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
    test_str="kipasa",
)

await DocumentTestModel.insert_one(document)
```

### Insert many documents

```python
document_1 = DocumentTestModel(
    test_int=42,
    test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
    test_str="kipasa",
)
document_2 = DocumentTestModel(
    test_int=42,
    test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
    test_str="kipasa",
)

await DocumentTestModel.insert_many([document_1, document_2])
```

## Find

### Get the document

```python
document = await DocumentTestModel.get(DOCUMENT_ID)
```

### Find one document

```python
document = await DocumentTestModel.find_one({"test_str": "kipasa"})
```

### Find many documents

```python
async for document in DocumentTestModel.find_many({"test_str": "uno"}, limit=100):
    print(document)
```

OR

```python
documents = await DocumentTestModel.find_many({"test_str": "uno"}, 
                                              sort="test_int").to_list()
```

Parameters:

- filter_query: The selection criteria
- skip: The number of documents to omit.
- limit: The maximum number of results to return.
- sort: A key or a list of (key, direction) pairs specifying the sort order for this query.

### Find all the documents

```python
async for document in DocumentTestModel.find_all(limit=100):
    print(document)
```

OR

```python
documents = await DocumentTestModel.find_all(skip=10).to_list()
```

Parameters:

- skip: The number of documents to omit.
- limit: The maximum number of results to return.
- sort: A key or a list of (key, direction) pairs specifying the sort order for this query.

## Update

### Replace the document (full update)

```python
document.test_str = "REPLACED_VALUE"
await document.replace()
```

### Replace one document

Replace one doc data by another

```python
new_doc = DocumentTestModel(
    test_int=0,
    test_str='REPLACED_VALUE',
    test_list=[]
)
await DocumentTestModel.replace_one({"_id": document.id}, new_doc)
```

### Update the document (partial update)

in this example, I'll add an item to the document's "test_list" field

```python
to_insert = SubDocument(test_str="test")
await document.update_dict(update_query={"$push": {"test_list": to_insert.dict()}})
```

### Update one document

```python
await DocumentTestModel.update_one(
    update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
    filter_query={"_id": document.id, "test_list.test_str": "foo"},
)
```

### Update many documents

```python
await DocumentTestModel.update_many(
    update_query={"$set": {"test_str": "bar"}},
    filter_query={"test_str": "foo"},
)
```

### Update all the documents

```python
await DocumentTestModel.update_all(
    update_query={"$set": {"test_str": "bar"}}
)
```

## Delete

### Delete the document

```python
await document.delete()
```

### Delete one documents

```python
await DocumentTestModel.delete_one({"test_str": "uno"})
```

### Delete many documents

```python
await DocumentTestModel.delete_many({"test_str": "dos"})
```

### Delete all the documents

```python
await DocumentTestModel.delete_all()
```

## Aggregate

```python
async for item in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
):
    print(item)
```

OR

```python
class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int


async for item in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputModel
):
    print(item)
```

OR

```python
results = await DocumentTestModel.aggregate(
    [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
    item_model=OutputModel
).to_list()
```

## Collection setup

Optionally collection of the document could be set up by the internal `Collection` class. Follow the examples:

### Collection name

The name of the collection could be set up by the field `name` of the Collection class. By default, the collection will
have the same name as the document class.

```python
class DocumentTestModelWithCustomCollectionName(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "custom_collection"
```

### Indexes

#### Single field indexes

To setup an index over a single field the `Indexed` function can be used to wrap the type:

```python
from beanie import Indexed

class DocumentTestModelWithIndex(Document):
    test_int: Indexed(int)
    test_list: List[SubDocument]
    test_str: str
```

The `Indexed` function takes an optional argument `index_type`, which may be set to a pymongo index type:
```python
test_str: Indexed(str, index_type = pymongo.TEXT)
```


#### Complex indexes
More complex indexes can be set up by the `indexes` field in a Collection class. It is a list where items could be:

- single key. Name of the document's field (this is equivalent to using the Indexed function described above)
- list of (key, direction) pairs. Key - string, name of the document's field. Direction - pymongo direction (
  example: `pymongo.ASCENDING`)
- `pymongo.IndexModel` instance - the most flexible
  option. [Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/operations.html#pymongo.operations.IndexModel)

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

## Use Motor Collection

In case, when you need more low-level control, you can get access to the engine of the Beanie `Document`- [AsyncIO Motor Collection](https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html)

```python
motor_collection = DocumentTestModel.get_motor_collection()
await motor_collection.drop_index("index_name")
```
   
