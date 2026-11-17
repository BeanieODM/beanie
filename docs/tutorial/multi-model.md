# Multi-model pattern

Documents with different schemas could be stored in a single collection and managed correctly. 
`UnionDoc` class is used for this.

It supports `find` and `aggregate` methods. 
For `find`, it will fetch all the found documents into the respective `Document` classes.

Documents with `union_doc` in their settings can still be used in `find` and other queries. 
Queries of one such class will not see the data of others.

## Example

Create documents:

```python
from beanie import Document, UnionDoc


class Parent(UnionDoc):  # Union
    class Settings:
        name = "union_doc_collection"  # Collection name
        class_id = "_class_id"  # _class_id is the default beanie internal field used to filter children Documents
        
        
class One(Document):
    int_field: int = 0
    shared: int = 0        

    class Settings:
        name = "One" # Name used to filer union document 'One', default to class name
        union_doc = Parent


class Two(Document):
    str_field: str = "test"
    shared: int = 0

    class Settings:
        union_doc = Parent
```

The schemas could be incompatible.

Insert a document

```python
await One().insert()
await One().insert()
await One().insert()

await Two().insert()
```

Find all the documents of the first type:

```python
docs = await One.all().to_list()
print(len(docs))

>> 3 # It found only documents of class One
```

Of the second type:

```python
docs = await Two.all().to_list()
print(len(docs))

>> 1 # It found only documents of class Two
```

Of both:

```python
docs = await Parent.all().to_list()
print(len(docs))

>> 4 # instances of both classes will be in the output here
```

Aggregations will work separately for these two document classes too.

## Discriminator field

`UnionDoc` keeps the class of each document in one field of the collection.

- `class_id` in the union's `Settings` is the **name** of that field. It defaults to `_class_id`.
- `name` in a member's `Settings` is the **value** written to that field. It defaults to the class name.
  Members are stored in the union's collection, so `name` is not a collection name here.
- Members take `class_id` from their union. Set it once, on the union.

A custom field name is useful when the collection already has a type field,
for example when other services write to it:

```python
class Event(UnionDoc):
    class Settings:
        name = "events"  # Collection name
        class_id = "type"  # Discriminator field


class Created(Document):
    created_at: datetime

    class Settings:
        name = "created"  # Stored as {"type": "created"}
        union_doc = Event


class Deleted(Document):
    deleted_at: datetime

    class Settings:
        name = "deleted"  # Stored as {"type": "deleted"}
        union_doc = Event
```

`Created.find()` adds `{"type": "created"}` to the query, `Created().insert()` writes it,
and `Event.find()` picks the class of each document by its `type` value.
