## beanie.odm.queries.find

## FindQuery

```python
class FindQuery(UpdateMethods,  SessionMethods)
```

Find Query base class

Inherited from:

- [SessionMethods](/beanie/api/interfaces/#sessionmethods)
- [UpdateMethods](/beanie/api/interfaces/#aggregatemethods)

### update

```python
def update(
	self, 
	*args: Union[dict, Mapping], 
	session: Optional[ClientSession] = None
)
```

Create Update with modifications query
and provide search criteria there

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

### delete

```python
def delete(
	self, 
	session: Optional[ClientSession] = None
) -> Union[DeleteOne, DeleteMany]
```

Provide search criteria to the Delete query

**Arguments**:

- `session`: Optional[ClientSession]

**Returns**:

Union[DeleteOne, DeleteMany]

### project

```python
def project(
	self, 
	projection_model: Optional[Type[BaseModel]]
)
```

Apply projection parameter

**Arguments**:

- `projection_model`: Optional[Type[BaseModel]] - projection model

**Returns**:

self

## FindMany

```python
class FindMany(BaseCursorQuery,  FindQuery,  AggregateMethods)
```

Find Many query class

Inherited from:

- [FindQuery](/beanie/api/queries/#findquery)
- [BaseCursorQuery](/beanie/api/queries/#basecursorquery) - async generator
- [AggregateMethods](/beanie/api/interfaces/#aggregatemethods)

### find\_many

```python
def find_many(
	self, 
	*args, 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
)
```

Find many documents by criteria

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

FindMany - query instance

### find

```python
def find(
	self, 
	*args, 
	skip: Optional[int] = None, 
	limit: Optional[int] = None, 
	sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
)
```

The same as `find_many(...)`

### sort

```python
def sort(
	self, 
	*args
)
```

Add sort parameters

**Arguments**:

- `args`: A key or a list of (key, direction) pairs specifying
the sort order for this query.

**Returns**:

self

### skip

```python
def skip(
	self, 
	n: Optional[int]
)
```

Set skip parameter

**Arguments**:

- `n`: int

**Returns**:

self

### limit

```python
def limit(
	self, 
	n: Optional[int]
)
```

Set limit parameter

**Arguments**:

- `n`: int

**Returns**:



### update\_many

```python
def update_many(
	self, 
	*args: Union[dict, Mapping], 
	session: Optional[ClientSession] = None
) -> UpdateMany
```

Provide search criteria to the
[UpdateMany](/beanie/api/queries/#updatemany) query

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

[UpdateMany](/beanie/api/queries/#updatemany) query

### delete\_many

```python
def delete_many(
	self, 
	session: Optional[ClientSession] = None
) -> DeleteMany
```

Provide search criteria to the [DeleteMany](/beanie/api/queries/#deletemany) query

**Arguments**:

- `session`: 

**Returns**:

[DeleteMany](/beanie/api/queries/#deletemany) query

### count

```python
async def count(
	self
) -> int
```

Number of found documents

**Returns**:

int

### aggregate

```python
def aggregate(
	self, 
	aggregation_pipeline: list, 
	projection_model: Type[BaseModel] = None, 
	session: Optional[ClientSession] = None
) -> AggregationQuery
```

Provide search criteria to the [AggregationQuery](/beanie/api/queries/#aggregationquery)

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline. MongoDB doc:
<https://docs.mongodb.com/manual/core/aggregation-pipeline/>
- `projection_model`: Type[BaseModel] - Projection Model
- `session`: Optional[ClientSession] - PyMongo session

**Returns**:

[AggregationQuery](/beanie/api/queries/#aggregationquery)

## FindOne

```python
class FindOne(FindQuery)
```

Find One query class

Inherited from:

- [FindQuery](/beanie/api/queries/#findquery)

### find\_one

```python
def find_one(
	self, 
	*args, 
	projection_model: Optional[Type[BaseModel]] = None, 
	session: Optional[ClientSession] = None
)
```

Find one document by criteria

**Arguments**:

- `args`: *Union[dict, Mapping] - search criteria
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

FindOne - query instance

### update\_one

```python
def update_one(
	self, 
	*args, 
	session: Optional[ClientSession] = None
) -> UpdateOne
```

Create [UpdateOne](/beanie/api/queries/#updateone) query using modifications and
provide search criteria there

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply
- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

[UpdateOne](/beanie/api/queries/#updateone) query

### delete\_one

```python
def delete_one(
	self, 
	session: Optional[ClientSession] = None
) -> DeleteOne
```

Provide search criteria to the [DeleteOne](/beanie/api/queries/#deleteone) query

**Arguments**:

- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

[DeleteOne](/beanie/api/queries/#deleteone) query

### replace\_one

```python
async def replace_one(
	self, 
	document, 
	session: Optional[ClientSession] = None
) -> UpdateResult
```

Replace found document by provided

**Arguments**:

- `document`: Document - document, which will replace the found one
- `session`: Optional[ClientSession] - PyMongo session

**Returns**:

UpdateResult

### \_\_await\_\_

```python
def __await__(
	self
)
```

Run the query

**Returns**:

Document

## beanie.odm.queries.update

## UpdateQuery

```python
class UpdateQuery(UpdateMethods,  SessionMethods)
```

Update Query base class

Inherited from:

- [SessionMethods](/beanie/api/interfaces/#sessionmethods)
- [UpdateMethods](/beanie/api/interfaces/#aggregatemethods)

### update

```python
def update(
	self, 
	*args: Union[dict, Mapping], 
	session: Optional[ClientSession] = None
)
```

Provide modifications to the update query. The same as `update()`

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

## UpdateMany

```python
class UpdateMany(UpdateQuery)
```

Update Many query class

Inherited from:

- [UpdateQuery](/beanie/api/queries/#updatequery)

### update\_many

```python
def update_many(
	self, 
	*args, 
	session: Optional[ClientSession] = None
)
```

Provide modifications to the update query

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

### \_\_await\_\_

```python
def __await__(
	self
)
```

Run the query

**Returns**:



## UpdateOne

```python
class UpdateOne(UpdateQuery)
```

Update One query class

Inherited from:

- [UpdateQuery](/beanie/api/queries/#updatequery)

### update\_one

```python
def update_one(
	self, 
	*args, 
	session: Optional[ClientSession] = None
)
```

Provide modifications to the update query. The same as `update()`

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

### \_\_await\_\_

```python
def __await__(
	self
)
```

Run the query

**Returns**:



## beanie.odm.queries.delete

## DeleteQuery

```python
class DeleteQuery(SessionMethods)
```

Deletion Query

## DeleteMany

```python
class DeleteMany(DeleteQuery)
```

### \_\_await\_\_

```python
def __await__(
	self
)
```

Run the query

**Returns**:



## DeleteOne

```python
class DeleteOne(DeleteQuery)
```

### \_\_await\_\_

```python
def __await__(
	self
)
```

Run the query

**Returns**:



## beanie.odm.queries.aggregation

## AggregationQuery

```python
class AggregationQuery(BaseCursorQuery,  SessionMethods)
```

Aggregation Query

Inherited from:

- [SessionMethods](/beanie/api/interfaces/#sessionmethods) - session methods
- [BaseCursorQuery](/beanie/api/queries/#basecursorquery) - async generator

## beanie.odm.queries.cursor

## BaseCursorQuery

```python
class BaseCursorQuery()
```

BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
which parse result with model

### to\_list

```python
async def to_list(
	self, 
	length: Optional[int] = None
) -> Union[List["Document"], List[dict]]
```

Get list of documents

**Arguments**:

- `length`: Optional[int] - length of the list

**Returns**:

Union[List["Document"], List[dict]]

