## beanie.odm.documents

## Document

```python
class Document(BaseModel,  UpdateMethods)
```

Document Mapping class.

Fields:

- `id` - MongoDB document ObjectID "_id" field.
Mapped to the PydanticObjectId class

Inherited from:

- Pydantic BaseModel
- [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)

### insert

```python
async def insert(
	self, 
	session: Optional[ClientSession] = None
) -> DocType
```

Insert the document (self) to the collection

**Returns**:

Document

### create

```python
async def create(
	self, 
	session: Optional[ClientSession] = None
) -> DocType
```

The same as self.insert()

**Returns**:

Document

### insert\_one

```python
@classmethod
async def insert_one(
	cls: Type[DocType], 
	document: DocType, 
	session: Optional[ClientSession] = None
) -> InsertOneResult
```

Insert one document to the collection

**Arguments**:

- `document`: Document - document to insert
- `session`: ClientSession - pymongo session

**Returns**:

InsertOneResult

### insert\_many

```python
@classmethod
async def insert_many(
	cls: Type[DocType], 
	documents: List[DocType], 
	keep_ids: bool = False, 
	session: Optional[ClientSession] = None
) -> InsertManyResult
```

Insert many documents to the collection

**Arguments**:

- `documents`: List["Document"] - documents to insert
- `keep_ids`: bool - should it insert documents with ids
or ignore it? Default False - ignore
- `session`: ClientSession - pymongo session

**Returns**:

InsertManyResult

### get

```python
@classmethod
async def get(
	cls: Type[DocType], 
	document_id: PydanticObjectId, 
	session: Optional[ClientSession] = None
) -> Optional[DocType]
```

Get document by id

**Arguments**:

- `document_id`: PydanticObjectId - document id
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

Union["Document", None]

### find\_one

```python
@classmethod
def find_one(
	cls, 
	*args: Union[Dict[str, Any], Mapping[str, Any], bool], 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindOne
```

Find one document by criteria.
Returns [FindOne](https://roman-right.github.io/beanie/api/queries/#findone) query object

**Arguments**:

- `args`: *Union[Dict[str, Any],
Mapping[str, Any], bool] - search criteria
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session instance

**Returns**:

[FindOne](https://roman-right.github.io/beanie/api/queries/#findone) - find query instance

### find\_many

```python
@classmethod
def find_many(
	cls, 
	*args: Union[Dict[str, Any], Mapping[str, Any], bool], 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindMany
```

Find many documents by criteria.
Returns [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) query object

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

[FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance

### find

```python
@classmethod
def find(
	cls, 
	*args: Union[Dict[str, Any], Mapping[str, Any], bool], 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindMany
```

The same as find_many

### find\_all

```python
@classmethod
def find_all(
	cls, 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindMany
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

[FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance

### all

```python
@classmethod
def all(
	cls, 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindMany
```

the same as find_all

### replace

```python
async def replace(
	self, 
	session: Optional[ClientSession] = None
) -> DocType
```

Fully update the document in the database

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

None

### replace\_many

```python
@classmethod
async def replace_many(
	cls: Type[DocType], 
	documents: List[DocType], 
	session: Optional[ClientSession] = None
) -> None
```

Replace list of documents

**Arguments**:

- `documents`: List["Document"]
- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

None

### update

```python
async def update(
	self, 
	*args, 
	session: Optional[ClientSession] = None
) -> None
```

Partially update the document in the database

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

None

### update\_all

```python
@classmethod
def update_all(
	cls, 
	*args: Union[dict, Mapping], 
	session: Optional[ClientSession] = None
) -> UpdateMany
```

Partially update all the documents

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateMany query

### delete

```python
async def delete(
	self, 
	session: Optional[ClientSession] = None
) -> DeleteResult
```

Delete the document

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

### delete\_all

```python
@classmethod
async def delete_all(
	cls, 
	session: Optional[ClientSession] = None
) -> DeleteResult
```

Delete all the documents

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session.

**Returns**:

DeleteResult - pymongo DeleteResult instance.

### aggregate

```python
@classmethod
def aggregate(
	cls, 
	aggregation_pipeline: list, 
	aggregation_model: Type[BaseModel] = None, 
	session: Optional[ClientSession] = None
) -> AggregationQuery
```

Aggregate over collection.
Returns [AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery) query object

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline
- `aggregation_model`: Type[BaseModel]
- `session`: Optional[ClientSession]

**Returns**:

[AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery)

### count

```python
@classmethod
async def count(
	cls
) -> int
```

Number of documents in the collections
The same as find_all().count()

**Returns**:

int

### init\_collection

```python
@classmethod
async def init_collection(
	cls, 
	database: AsyncIOMotorDatabase, 
	allow_index_dropping: bool
) -> None
```

Internal CollectionMeta class creator

**Arguments**:

- `database`: AsyncIOMotorDatabase - motor database instance
- `allow_index_dropping`: bool - if index dropping is allowed

**Returns**:

None

### get\_motor\_collection

```python
@classmethod
def get_motor_collection(
	cls
) -> AsyncIOMotorCollection
```

Get Motor Collection to access low level control

**Returns**:

AsyncIOMotorCollection

### inspect\_collection

```python
@classmethod
async def inspect_collection(
	cls, 
	session: Optional[ClientSession] = None
) -> InspectionResult
```

Check, if documents, stored in the MongoDB collection
are compatible with the Document schema

**Returns**:

InspectionResult

