## beanie.odm.queries.find

## FindQuery

```python
class FindQuery(UpdateMethods,  SessionMethods)
```

Find Query base class

### update

```python
def update(
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
	session: Optional[ClientSession] = None
)
```

Provide search criteria to the Delete query

**Arguments**:

- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

### project

```python
def project(
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

- [FindQuery](/api/queries/#findquery)
- [BaseCursorQuery](/api/queries/#basecursorquery)
- [AggregateMethods](/api/interfaces/#aggregatemethods)

### find\_many

```python
def find_many(
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
	*args: Union[dict, Mapping], 
	session: Optional[ClientSession] = None
) -> UpdateMany
```

Provide search criteria to the update query

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

### delete\_many

```python
def delete_many(
	session: Optional[ClientSession] = None
) -> DeleteMany
```

Provide search criteria to the DeleteMany query

**Arguments**:

- `session`: 

**Returns**:

DeleteMany query

### count

```python
async def count(
) -> int
```

Number of found documents

**Returns**:

int

### aggregate

```python
def aggregate(
	aggregation_pipeline: list, 
	projection_model: Type[BaseModel] = None, 
	session: Optional[ClientSession] = None
) -> AggregationQuery
```

Provide search criteria to the AggregateQuery

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline. MongoDB doc:
<https://docs.mongodb.com/manual/core/aggregation-pipeline/>
- `projection_model`: Type[BaseModel] - Projection Model
- `session`: Optional[ClientSession] - PyMongo session

**Returns**:

AggregationQuery

## FindOne

```python
class FindOne(FindQuery)
```

Find One query class

### find\_one

```python
def find_one(
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
	*args, 
	session: Optional[ClientSession] = None
) -> UpdateOne
```

Create UpdateOne query using modifications and
provide search criteria there

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply
- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

UpdateOne query

### delete\_one

```python
def delete_one(
	session: Optional[ClientSession] = None
) -> DeleteOne
```

Provide search criteria to the DeleteOne query

**Arguments**:

- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

DeleteOne query

### replace\_one

```python
async def replace_one(
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

## UpdateMany

```python
class UpdateMany(UpdateQuery)
```

Update Many query class

## UpdateOne

```python
class UpdateOne(UpdateQuery)
```

Update One query class

## beanie.odm.queries.delete

## DeleteQuery

```python
class DeleteQuery(SessionMethods)
```

Deletion Query

## beanie.odm.queries.aggregation

## AggregationQuery

```python
class AggregationQuery(BaseCursorQuery,  SessionMethods)
```

Aggregation Query

It is async generator. Use `async for` or
`to_list` method to work with this

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
	length: Optional[int] = None
) -> Union[List["Document"], List[dict]]
```

Get list of documents

**Arguments**:

- `length`: Optional[int] - length of the list

**Returns**:

Union[List["Document"], List[dict]]

