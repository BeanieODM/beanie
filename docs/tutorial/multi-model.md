# Multi-model pattern

Documents with different schemes could be stored in a single collection and managed correctly. `UnionDoc` class is used for this.

It supports find and aggregate methods. For find it will fetch all the found documents into the respective `Document` classes.

Documents that have `union_doc` in the settings still can be used in find and other queries. Queries of one such class will not see data of others.

## Example

Create documents

```python
from beanie import Document, UnionDoc

class Parent(UnionDoc):  # Union
    class Settings:
        name = "union_doc_collection"  # Collection name

class One(Document):
    int_field: int = 0
    shared: int = 0        

    class Settings:
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

Find all the doc of the first type:

```python
docs = await One.all().to_list()
print(len(docs))

>> 3 # It found only documents of class One
```

Of the second type:

```python
docs = await Two.all().to_list()
print(len(docs))

>> 1 # It found only documents of class One
```

Of both:

```python
docs = await Parent.all().to_list()
print(len(docs))

>> 4 # instances of the both classes will be in the output here
```

Aggregations will work separately for these two document classes too.