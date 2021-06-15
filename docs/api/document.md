<a name="beanie.odm.documents"></a>
# beanie.odm.documents

<a name="beanie.odm.documents.Document"></a>
## Document Objects

```python
class Document(BaseModel,  UpdateMethods)
```

Document Mapping class.

Fields:

- `id` - MongoDB document ObjectID "_id" field.
Mapped to the PydanticObjectId class

Inherited from:

- Pydantic BaseModel
- [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/`aggregatemethods`)

<a name="beanie.odm.documents.Document.insert"></a>
#### insert

```python
 | async insert(session: Optional[ClientSession] = None) -> DocType
```

Insert the document (self) to the collection

**Returns**:

Document

<a name="beanie.odm.documents.Document.create"></a>
#### create

```python
 | async create(session: Optional[ClientSession] = None) -> DocType
```

The same as self.insert()

**Returns**:

Document

<a name="beanie.odm.documents.Document.insert_one"></a>
#### insert\_one

```python
 | @classmethod
 | async insert_one(cls: Type[DocType], document: DocType, session: Optional[ClientSession] = None) -> InsertOneResult
```

Insert one document to the collection

**Arguments**:

- `document`: Document - document to insert
- `session`: ClientSession - pymongo session

**Returns**:

InsertOneResult

<a name="beanie.odm.documents.Document.insert_many"></a>
#### insert\_many

```python
 | @classmethod
 | async insert_many(cls: Type[DocType], documents: List[DocType], session: Optional[ClientSession] = None) -> InsertManyResult
```

Insert many documents to the collection

**Arguments**:

- `documents`: List["Document"] - documents to insert
- `session`: ClientSession - pymongo session

**Returns**:

InsertManyResult

<a name="beanie.odm.documents.Document.get"></a>
#### get

```python
 | @classmethod
 | async get(cls: Type[DocType], document_id: PydanticObjectId, session: Optional[ClientSession] = None) -> Optional[DocType]
```

Get document by id

**Arguments**:

- `document_id`: PydanticObjectId - document id
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

Union["Document", None]

<a name="beanie.odm.documents.Document.find_one"></a>
#### find\_one

```python
 | @classmethod
 | find_one(cls, *args: Union[Dict[str, Any], Mapping[str, Any], bool], *, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> FindOne
```

Find one document by criteria.
Returns [FindOne](https://roman-right.github.io/beanie/api/queries/`findone`) query object

**Arguments**:

- `args`: *Union[Dict[str, Any],
Mapping[str, Any], bool] - search criteria
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session instance

**Returns**:

[FindOne](https://roman-right.github.io/beanie/api/queries/`findone`) - find query instance

<a name="beanie.odm.documents.Document.find_many"></a>
#### find\_many

```python
 | @classmethod
 | find_many(cls, *args: Union[Dict[str, Any], Mapping[str, Any], bool], *, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> FindMany
```

Find many documents by criteria.
Returns [FindMany](https://roman-right.github.io/beanie/api/queries/`findmany`) query object

**Arguments**:

- `args`: *Union[Dict[str, Any],
Mapping[str, Any], bool] - search criteria
- `skip`: Optional[int] - The number of documents to omit.
- `limit`: Optional[int] - The maximum number of results to return.
- `sort`: Union[None, str, List[Tuple[str, SortDirection]]] - A key
or a list of (key, direction) pairs specifying the sort order
for this query.
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

[FindMany](https://roman-right.github.io/beanie/api/queries/`findmany`) - query instance

<a name="beanie.odm.documents.Document.find"></a>
#### find

```python
 | @classmethod
 | find(cls, *args: Union[Dict[str, Any], Mapping[str, Any], bool], *, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> FindMany
```

The same as find_many

<a name="beanie.odm.documents.Document.find_all"></a>
#### find\_all

```python
 | @classmethod
 | find_all(cls, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> FindMany
```

Get all the documents

**Arguments**:

- `skip`: Optional[int] - The number of documents to omit.
- `limit`: Optional[int] - The maximum number of results to return.
- `sort`: Union[None, str, List[Tuple[str, SortDirection]]] - A key
or a list of (key, direction) pairs specifying the sort order
for this query.
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

[FindMany](https://roman-right.github.io/beanie/api/queries/`findmany`) - query instance

<a name="beanie.odm.documents.Document.all"></a>
#### all

```python
 | @classmethod
 | all(cls, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> FindMany
```

the same as find_all

<a name="beanie.odm.documents.Document.replace"></a>
#### replace

```python
 | async replace(session: Optional[ClientSession] = None) -> DocType
```

Fully update the document in the database

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

None

<a name="beanie.odm.documents.Document.save"></a>
#### save

```python
 | async save(session: Optional[ClientSession] = None) -> DocType
```

Update an existing model in the database or insert it if it does not yet exist.

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

None

<a name="beanie.odm.documents.Document.replace_many"></a>
#### replace\_many

```python
 | @classmethod
 | async replace_many(cls: Type[DocType], documents: List[DocType], session: Optional[ClientSession] = None) -> None
```

Replace list of documents

**Arguments**:

- `documents`: List["Document"]
- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

None

<a name="beanie.odm.documents.Document.update"></a>
#### update

```python
 | async update(*args, *, session: Optional[ClientSession] = None) -> None
```

Partially update the document in the database

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

None

<a name="beanie.odm.documents.Document.update_all"></a>
#### update\_all

```python
 | @classmethod
 | update_all(cls, *args: Union[dict, Mapping], *, session: Optional[ClientSession] = None) -> UpdateMany
```

Partially update all the documents

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateMany query

<a name="beanie.odm.documents.Document.delete"></a>
#### delete

```python
 | async delete(session: Optional[ClientSession] = None) -> DeleteResult
```

Delete the document

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

<a name="beanie.odm.documents.Document.delete_all"></a>
#### delete\_all

```python
 | @classmethod
 | async delete_all(cls, session: Optional[ClientSession] = None) -> DeleteResult
```

Delete all the documents

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

<a name="beanie.odm.documents.Document.aggregate"></a>
#### aggregate

```python
 | @classmethod
 | aggregate(cls, aggregation_pipeline: list, projection_model: Type[BaseModel] = None, session: Optional[ClientSession] = None) -> AggregationQuery
```

Aggregate over collection.
Returns [AggregationQuery](https://roman-right.github.io/beanie/api/queries/`aggregationquery`) query object

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline
- `projection_model`: Type[BaseModel]
- `session`: Optional[ClientSession]

**Returns**:

[AggregationQuery](https://roman-right.github.io/beanie/api/queries/`aggregationquery`)

<a name="beanie.odm.documents.Document.count"></a>
#### count

```python
 | @classmethod
 | async count(cls) -> int
```

Number of documents in the collections
The same as find_all().count()

**Returns**:

int

<a name="beanie.odm.documents.Document.init_collection"></a>
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

<a name="beanie.odm.documents.Document.get_motor_collection"></a>
#### get\_motor\_collection

```python
 | @classmethod
 | get_motor_collection(cls) -> AsyncIOMotorCollection
```

Get Motor Collection to access low level control

**Returns**:

AsyncIOMotorCollection

<a name="beanie.odm.documents.Document.inspect_collection"></a>
#### inspect\_collection

```python
 | @classmethod
 | async inspect_collection(cls, session: Optional[ClientSession] = None) -> InspectionResult
```

Check, if documents, stored in the MongoDB collection
are compatible with the Document schema

**Returns**:

InspectionResult

