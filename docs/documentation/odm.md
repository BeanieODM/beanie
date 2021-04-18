# Table of Contents

* [collection](#collection)
  * [collection\_factory](#collection.collection_factory)
* [general](#general)
  * [get\_model](#general.get_model)
  * [init\_beanie](#general.init_beanie)
* [documents](#documents)
  * [Document](#documents.Document)
    * [\_\_init\_\_](#documents.Document.__init__)
    * [insert\_one](#documents.Document.insert_one)
    * [insert\_many](#documents.Document.insert_many)
    * [create](#documents.Document.create)
    * [find\_one](#documents.Document.find_one)
    * [find\_many](#documents.Document.find_many)
    * [find\_all](#documents.Document.find_all)
    * [get](#documents.Document.get)
    * [replace\_one](#documents.Document.replace_one)
    * [replace\_many](#documents.Document.replace_many)
    * [replace](#documents.Document.replace)
    * [update\_one](#documents.Document.update_one)
    * [update\_many](#documents.Document.update_many)
    * [update\_all](#documents.Document.update_all)
    * [update](#documents.Document.update)
    * [delete\_one](#documents.Document.delete_one)
    * [delete\_many](#documents.Document.delete_many)
    * [delete\_all](#documents.Document.delete_all)
    * [delete](#documents.Document.delete)
    * [aggregate](#documents.Document.aggregate)
    * [count\_documents](#documents.Document.count_documents)
    * [init\_collection](#documents.Document.init_collection)
    * [get\_motor\_collection](#documents.Document.get_motor_collection)
    * [inspect\_collection](#documents.Document.inspect_collection)
* [\_\_init\_\_](#__init__)
* [cursor](#cursor)
  * [Cursor](#cursor.Cursor)
    * [to\_list](#cursor.Cursor.to_list)
* [models](#models)
  * [SortDirection](#models.SortDirection)
  * [FindOperationKWARGS](#models.FindOperationKWARGS)
  * [InspectionStatuses](#models.InspectionStatuses)
  * [InspectionError](#models.InspectionError)
  * [InspectionResult](#models.InspectionResult)
* [fields](#fields)
  * [Indexed](#fields.Indexed)
  * [PydanticObjectId](#fields.PydanticObjectId)

<a name="collection"></a>
# collection

<a name="collection.collection_factory"></a>
#### collection\_factory

```python
async collection_factory(database: AsyncIOMotorDatabase, document_class: Type, allow_index_dropping: bool, collection_class: Optional[Type] = None) -> Type
```

Collection factory.
Creates internal CollectionMeta class for the Document on the init step,

**Arguments**:

- `database`: AsyncIOMotorDatabase - Motor database instance
- `document_class`: Type - a class, inherited from Document class
- `allow_index_dropping`: bool - if index dropping is allowed
- `collection_class`: Optional[Type] - Collection, which was set up by user

**Returns**:

Type - Collection class

<a name="general"></a>
# general

<a name="general.get_model"></a>
#### get\_model

```python
get_model(dot_path: str) -> Type[Document]
```

Get the model by the path in format bar.foo.Model

**Arguments**:

- `dot_path`: str - dot seprated path to the model

**Returns**:

Type[Document] - class of the model

<a name="general.init_beanie"></a>
#### init\_beanie

```python
async init_beanie(database: AsyncIOMotorDatabase, document_models: List[Union[Type[Document], str]], allow_index_dropping: bool = True)
```

Beanie initialization

**Arguments**:

- `database`: AsyncIOMotorDatabase - motor database instance
- `document_models`: List[Union[Type[Document], str]] - model
classes or strings with dot separated paths
- `allow_index_dropping`: bool - if index dropping is allowed. Default True

**Returns**:

None

<a name="documents"></a>
# documents

<a name="documents.Document"></a>
## Document Objects

```python
class Document(BaseModel)
```

Document Mapping class.

Inherited from Pydantic BaseModel ß includes all the respective methods.
Contains id filed - MongoDB document ObjectID "_id" field

<a name="documents.Document.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(*args, **kwargs)
```

Initialization

**Arguments**:

- `args`: 
- `kwargs`: 

<a name="documents.Document.insert_one"></a>
#### insert\_one

```python
 | @classmethod
 | async insert_one(cls, document: "Document", session: ClientSession = None) -> InsertOneResult
```

Insert one document to the collection

**Arguments**:

- `document`: Document - document to insert
- `session`: ClientSession - pymongo session

**Returns**:

Document

<a name="documents.Document.insert_many"></a>
#### insert\_many

```python
 | @classmethod
 | async insert_many(cls, documents: List["Document"], keep_ids: bool = False, session: ClientSession = None)
```

Insert many documents to the collection

**Arguments**:

- `documents`: List["Document"] - documents to insert
- `keep_ids`: bool - should it insert documents with ids or ignore it? Default False - ignore
- `session`: ClientSession - pymongo session

**Returns**:

Document

<a name="documents.Document.create"></a>
#### create

```python
 | async create(session: ClientSession = None) -> "Document"
```

Create the document in the database

**Returns**:

Document

<a name="documents.Document.find_one"></a>
#### find\_one

```python
 | @classmethod
 | async find_one(cls, filter_query: dict, session: ClientSession = None) -> Union["Document", None]
```

Find one document by criteria

**Arguments**:

- `filter_query`: dict - The selection criteria

**Returns**:

Union["Document", None]

<a name="documents.Document.find_many"></a>
#### find\_many

```python
 | @classmethod
 | find_many(cls, filter_query: dict, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, session: ClientSession = None) -> Cursor
```

Find many documents by criteria

**Arguments**:

- `filter_query`: dict - The selection criteria.
- `skip`: Optional[int] - The number of documents to omit.
- `limit`: Optional[int] - The maximum number of results to return.
- `sort`: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs
             specifying the sort order for this query.
- `session`: ClientSession - pymongo session

**Returns**:

Cursor - AsyncGenerator of the documents

<a name="documents.Document.find_all"></a>
#### find\_all

```python
 | @classmethod
 | find_all(cls, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, session: ClientSession = None) -> Cursor
```

Get all the documents

**Arguments**:

- `skip`: Optional[int] - The number of documents to omit.
- `limit`: Optional[int] - The maximum number of results to return.
- `sort`: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs
             specifying the sort order for this query.
- `session`: ClientSession - pymongo session

**Returns**:

Cursor - AsyncGenerator of the documents

<a name="documents.Document.get"></a>
#### get

```python
 | @classmethod
 | async get(cls, document_id: PydanticObjectId, session: ClientSession = None) -> Union["Document", None]
```

Get document by id

**Returns**:

Union["Document", None]

<a name="documents.Document.replace_one"></a>
#### replace\_one

```python
 | @classmethod
 | async replace_one(cls, filter_query: dict, document: "Document", session: ClientSession = None)
```

Fully update one document in the database

**Arguments**:

- `filter_query`: dict - the selection criteria.
- `document`: Document - the document which will replace the found one.
- `session`: ClientSession - pymongo session.

**Returns**:

None

<a name="documents.Document.replace_many"></a>
#### replace\_many

```python
 | @classmethod
 | async replace_many(cls, documents: List["Document"], session: ClientSession = None) -> None
```

**Arguments**:

- `documents`: List["Document"]
- `session`: ClientSession - pymongo session.

**Returns**:

None

<a name="documents.Document.replace"></a>
#### replace

```python
 | async replace(session: ClientSession = None) -> "Document"
```

Fully update the document in the database

**Arguments**:

- `session`: ClientSession - pymongo session.

**Returns**:

None

<a name="documents.Document.update_one"></a>
#### update\_one

```python
 | @classmethod
 | async update_one(cls, filter_query: dict, update_query: dict, session: ClientSession = None) -> UpdateResult
```

Partially update already created document

**Arguments**:

- `filter_query`: dict - the modifications to apply.
- `update_query`: dict - the selection criteria for the update.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateResult - pymongo UpdateResult instance

<a name="documents.Document.update_many"></a>
#### update\_many

```python
 | @classmethod
 | async update_many(cls, filter_query: dict, update_query: dict, session: ClientSession = None) -> UpdateResult
```

Partially update many documents

**Arguments**:

- `filter_query`: dict - the selection criteria for the update.
- `update_query`: dict - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateResult - pymongo UpdateResult instance

<a name="documents.Document.update_all"></a>
#### update\_all

```python
 | @classmethod
 | async update_all(cls, update_query: dict, session: ClientSession = None) -> UpdateResult
```

Partially update all the documents

**Arguments**:

- `update_query`: dict - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateResult - pymongo UpdateResult instance

<a name="documents.Document.update"></a>
#### update

```python
 | async update(update_query: dict, session: ClientSession = None) -> None
```

Partially update the document in the database

**Arguments**:

- `update_query`: dict - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

None

<a name="documents.Document.delete_one"></a>
#### delete\_one

```python
 | @classmethod
 | async delete_one(cls, filter_query: dict, session: ClientSession = None) -> DeleteResult
```

Delete one document

**Arguments**:

- `filter_query`: dict - the selection criteria
- `session`: ClientSession - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance

<a name="documents.Document.delete_many"></a>
#### delete\_many

```python
 | @classmethod
 | async delete_many(cls, filter_query: dict, session: ClientSession = None) -> DeleteResult
```

Delete many documents

**Arguments**:

- `filter_query`: dict - the selection criteria.
- `session`: ClientSession - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

<a name="documents.Document.delete_all"></a>
#### delete\_all

```python
 | @classmethod
 | async delete_all(cls, session: ClientSession = None) -> DeleteResult
```

Delete all the documents

**Arguments**:

- `session`: ClientSession - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

<a name="documents.Document.delete"></a>
#### delete

```python
 | async delete(session: ClientSession = None) -> DeleteResult
```

Delete the document

**Arguments**:

- `session`: ClientSession - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

<a name="documents.Document.aggregate"></a>
#### aggregate

```python
 | @classmethod
 | aggregate(cls, aggregation_query: List[dict], item_model: Type[BaseModel] = None, session: ClientSession = None) -> Cursor
```

Aggregate

**Arguments**:

- `aggregation_query`: List[dict] - query with aggregation commands
- `item_model`: Type[BaseModel] - model of item to return in the list of aggregations
- `session`: ClientSession - pymongo session.

**Returns**:

Cursor - AsyncGenerator of aggregated items

<a name="documents.Document.count_documents"></a>
#### count\_documents

```python
 | @classmethod
 | async count_documents(cls, filter_query: Optional[dict] = None) -> int
```

Number of documents in the collections

**Arguments**:

- `filter_query`: dict - the selection criteria

**Returns**:

int

<a name="documents.Document.init_collection"></a>
#### init\_collection

```python
 | @classmethod
 | async init_collection(cls, database: AsyncIOMotorDatabase, allow_index_dropping: bool) -> None
```

Internal CollectionMeta class creator

**Arguments**:

- `database`: AsyncIOMotorDatabase - motor database instance
- `allow_index_dropping`: bool - if index dropping is allowed

**Returns**:

None

<a name="documents.Document.get_motor_collection"></a>
#### get\_motor\_collection

```python
 | @classmethod
 | get_motor_collection(cls) -> AsyncIOMotorCollection
```

Get Motor Collection to access low level control

**Returns**:

AsyncIOMotorCollection

<a name="documents.Document.inspect_collection"></a>
#### inspect\_collection

```python
 | @classmethod
 | async inspect_collection(cls, session: ClientSession = None) -> InspectionResult
```

Check, if documents, stored in the MongoDB collection
are compatible with the Document schema

**Returns**:

InspectionResult

<a name="__init__"></a>
# \_\_init\_\_

<a name="cursor"></a>
# cursor

<a name="cursor.Cursor"></a>
## Cursor Objects

```python
class Cursor()
```

Cursor class. Wrapper over AsyncIOMotorCursor, which parse result with model

<a name="cursor.Cursor.to_list"></a>
#### to\_list

```python
 | async to_list(length: Optional[int] = None) -> Union[List["Document"], List[dict]]
```

Get list of documents

**Arguments**:

- `length`: Optional[int] - length of the list

**Returns**:

Union[List["Document"], List[dict]]

<a name="models"></a>
# models

<a name="models.SortDirection"></a>
## SortDirection Objects

```python
class SortDirection(int,  Enum)
```

Sorting directions

<a name="models.FindOperationKWARGS"></a>
## FindOperationKWARGS Objects

```python
class FindOperationKWARGS(BaseModel)
```

KWARGS Parser for find operations

<a name="models.InspectionStatuses"></a>
## InspectionStatuses Objects

```python
class InspectionStatuses(str,  Enum)
```

Statuses of the collection inspection

<a name="models.InspectionError"></a>
## InspectionError Objects

```python
class InspectionError(BaseModel)
```

Inspection error details

<a name="models.InspectionResult"></a>
## InspectionResult Objects

```python
class InspectionResult(BaseModel)
```

Collection inspection result

<a name="fields"></a>
# fields

<a name="fields.Indexed"></a>
#### Indexed

```python
Indexed(typ, index_type=ASCENDING)
```

Returns a subclass of `typ` with an extra attribute `_indexed` et to True.
When instantiated the type of the result will actually be `typ`.

<a name="fields.PydanticObjectId"></a>
## PydanticObjectId Objects

```python
class PydanticObjectId(ObjectId)
```

Object Id field. Compatible with Pydantic.

