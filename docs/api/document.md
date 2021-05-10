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
- [UpdateMethods](/beanie/api/interfaces/#aggregatemethods)

### insert

```python
async def insert(
	self, 
	session: Optional[ClientSession] = None
) -> "Document"
```

Insert the document (self) to the collection

**Returns**:

Document

### create

```python
async def create(
	self, 
	session: Optional[ClientSession] = None
) -> "Document"
```

The same as self.insert()

**Returns**:

Document

### insert\_one

```python
@classmethod
async def insert_one(
	cls, 
	document: "Document", 
	session: Optional[ClientSession] = None
) -> InsertOneResult
```

Insert one document to the collection

**Arguments**:

- `document`: Document - document to insert
- `session`: ClientSession - pymongo session

**Returns**:

Document

### insert\_many

```python
@classmethod
async def insert_many(
	cls, 
	documents: List["Document"], 
	keep_ids: bool = False, 
	session: Optional[ClientSession] = None
)
```

Insert many documents to the collection

**Arguments**:

- `documents`: List["Document"] - documents to insert
- `keep_ids`: bool - should it insert documents with ids
or ignore it? Default False - ignore
- `session`: ClientSession - pymongo session

**Returns**:

Document

### get

```python
@classmethod
async def get(
	cls, 
	document_id: PydanticObjectId, 
	session: Optional[ClientSession] = None
) -> Union["Document", None]
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
	*args: Union[dict, Mapping], 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindOne
```

Find one document by criteria.
Returns [FindOne](/beanie/api/queries/#findone) query object

**Arguments**:

- `args`: *Union[dict, Mapping] - search criteria
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session instance

**Returns**:

[FindOne](/beanie/api/queries/#findone) - find query instance

### find\_many

```python
@classmethod
def find_many(
	cls, 
	*args, 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
) -> FindMany
```

Find many documents by criteria.
Returns [FindMany](/beanie/api/queries/#findmany) query object

**Arguments**:

- `args`: *Union[dict, Mapping] - search criteria
- `skip`: Optional[int] - The number of documents to omit.
- `limit`: Optional[int] - The maximum number of results to return.
- `sort`: Union[None, str, List[Tuple[str, SortDirection]]] - A key
or a list of (key, direction) pairs specifying the sort order
for this query.
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

[FindMany](/beanie/api/queries/#findmany) - query instance

### find

```python
@classmethod
def find(
	cls, 
	*args, 
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

[FindMany](/beanie/api/queries/#findmany) - query instance

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
) -> "Document"
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
	cls, 
	documents: List["Document"], 
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
) -> UpdateResult
```

Partially update all the documents

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: ClientSession - pymongo session.

**Returns**:

UpdateResult - pymongo UpdateResult instance

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
Returns [AggregationQuery](/beanie/api/queries/#aggregationquery) query object

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline
- `aggregation_model`: Type[BaseModel]
- `session`: Optional[ClientSession]

**Returns**:

[AggregationQuery](/beanie/api/queries/#aggregationquery)

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

