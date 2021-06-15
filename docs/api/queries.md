<a name="beanie.odm.queries.find"></a>
# beanie.odm.queries.find

<a name="beanie.odm.queries.find.FindQuery"></a>
## FindQuery Objects

```python
class FindQuery(UpdateMethods,  SessionMethods)
```

Find Query base class

Inherited from:

- [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/`sessionmethods`)
- [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/`aggregatemethods`)

<a name="beanie.odm.queries.find.FindQuery.update"></a>
#### update

```python
 | update(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None)
```

Create Update with modifications query
and provide search criteria there

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

<a name="beanie.odm.queries.find.FindQuery.delete"></a>
#### delete

```python
 | delete(session: Optional[ClientSession] = None) -> Union[DeleteOne, DeleteMany]
```

Provide search criteria to the Delete query

**Arguments**:

- `session`: Optional[ClientSession]

**Returns**:

Union[DeleteOne, DeleteMany]

<a name="beanie.odm.queries.find.FindQuery.project"></a>
#### project

```python
 | project(projection_model: Optional[Type[BaseModel]]) -> FindQueryType
```

Apply projection parameter

**Arguments**:

- `projection_model`: Optional[Type[BaseModel]] - projection model

**Returns**:

self

<a name="beanie.odm.queries.find.FindMany"></a>
## FindMany Objects

```python
class FindMany(FindQuery,  BaseCursorQuery,  AggregateMethods)
```

Find Many query class

Inherited from:

- [FindQuery](https://roman-right.github.io/beanie/api/queries/`findquery`)
- [BaseCursorQuery](https://roman-right.github.io/beanie/api/queries/`basecursorquery`) - async generator
- [AggregateMethods](https://roman-right.github.io/beanie/api/interfaces/`aggregatemethods`)

<a name="beanie.odm.queries.find.FindMany.find_many"></a>
#### find\_many

```python
 | find_many(*args: Union[Dict[str, Any], Mapping[str, Any], bool], *, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> "FindMany"
```

Find many documents by criteria

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

FindMany - query instance

<a name="beanie.odm.queries.find.FindMany.find"></a>
#### find

```python
 | find(*args: Union[Dict[str, Any], Mapping[str, Any], bool], *, skip: Optional[int] = None, limit: Optional[int] = None, sort: Union[None, str, List[Tuple[str, SortDirection]]] = None, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> "FindMany"
```

The same as `find_many(...)`

<a name="beanie.odm.queries.find.FindMany.sort"></a>
#### sort

```python
 | sort(*args: Optional[
 |             Union[
 |                 str, Tuple[str, SortDirection], List[Tuple[str, SortDirection]]
 |             ]
 |         ]) -> "FindMany"
```

Add sort parameters

**Arguments**:

- `args`: Union[str, Tuple[str, SortDirection],
List[Tuple[str, SortDirection]]] - A key or a tuple (key, direction)
or a list of (key, direction) pairs specifying
the sort order for this query.

**Returns**:

self

<a name="beanie.odm.queries.find.FindMany.skip"></a>
#### skip

```python
 | skip(n: Optional[int]) -> "FindMany"
```

Set skip parameter

**Arguments**:

- `n`: int

**Returns**:

self

<a name="beanie.odm.queries.find.FindMany.limit"></a>
#### limit

```python
 | limit(n: Optional[int]) -> "FindMany"
```

Set limit parameter

**Arguments**:

- `n`: int

**Returns**:



<a name="beanie.odm.queries.find.FindMany.update_many"></a>
#### update\_many

```python
 | update_many(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None) -> UpdateMany
```

Provide search criteria to the
[UpdateMany](https://roman-right.github.io/beanie/api/queries/`updatemany`) query

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

[UpdateMany](https://roman-right.github.io/beanie/api/queries/`updatemany`) query

<a name="beanie.odm.queries.find.FindMany.delete_many"></a>
#### delete\_many

```python
 | delete_many(session: Optional[ClientSession] = None) -> DeleteMany
```

Provide search criteria to the [DeleteMany](https://roman-right.github.io/beanie/api/queries/`deletemany`) query

**Arguments**:

- `session`: 

**Returns**:

[DeleteMany](https://roman-right.github.io/beanie/api/queries/`deletemany`) query

<a name="beanie.odm.queries.find.FindMany.count"></a>
#### count

```python
 | async count() -> int
```

Number of found documents

**Returns**:

int

<a name="beanie.odm.queries.find.FindMany.aggregate"></a>
#### aggregate

```python
 | aggregate(aggregation_pipeline: List[Any], projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> AggregationQuery
```

Provide search criteria to the [AggregationQuery](https://roman-right.github.io/beanie/api/queries/`aggregationquery`)

**Arguments**:

- `aggregation_pipeline`: list - aggregation pipeline. MongoDB doc:
<https://docs.mongodb.com/manual/core/aggregation-pipeline/>
- `projection_model`: Type[BaseModel] - Projection Model
- `session`: Optional[ClientSession] - PyMongo session

**Returns**:

[AggregationQuery](https://roman-right.github.io/beanie/api/queries/`aggregationquery`)

<a name="beanie.odm.queries.find.FindOne"></a>
## FindOne Objects

```python
class FindOne(FindQuery)
```

Find One query class

Inherited from:

- [FindQuery](https://roman-right.github.io/beanie/api/queries/`findquery`)

<a name="beanie.odm.queries.find.FindOne.find_one"></a>
#### find\_one

```python
 | find_one(*args: Union[Dict[str, Any], Mapping[str, Any], bool], *, projection_model: Optional[Type[BaseModel]] = None, session: Optional[ClientSession] = None) -> "FindOne"
```

Find one document by criteria

**Arguments**:

- `args`: *Union[Dict[str, Any], Mapping[str, Any],
bool] - search criteria
- `projection_model`: Optional[Type[BaseModel]] - projection model
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

FindOne - query instance

<a name="beanie.odm.queries.find.FindOne.update_one"></a>
#### update\_one

```python
 | update_one(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None) -> UpdateOne
```

Create [UpdateOne](https://roman-right.github.io/beanie/api/queries/`updateone`) query using modifications and
provide search criteria there

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply
- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

[UpdateOne](https://roman-right.github.io/beanie/api/queries/`updateone`) query

<a name="beanie.odm.queries.find.FindOne.delete_one"></a>
#### delete\_one

```python
 | delete_one(session: Optional[ClientSession] = None) -> DeleteOne
```

Provide search criteria to the [DeleteOne](https://roman-right.github.io/beanie/api/queries/`deleteone`) query

**Arguments**:

- `session`: Optional[ClientSession] - PyMongo sessions

**Returns**:

[DeleteOne](https://roman-right.github.io/beanie/api/queries/`deleteone`) query

<a name="beanie.odm.queries.find.FindOne.replace_one"></a>
#### replace\_one

```python
 | async replace_one(document: "DocType", session: Optional[ClientSession] = None) -> UpdateResult
```

Replace found document by provided

**Arguments**:

- `document`: Document - document, which will replace the found one
- `session`: Optional[ClientSession] - PyMongo session

**Returns**:

UpdateResult

<a name="beanie.odm.queries.find.FindOne.__await__"></a>
#### \_\_await\_\_

```python
 | __await__()
```

Run the query

**Returns**:

BaseModel

<a name="beanie.odm.queries.update"></a>
# beanie.odm.queries.update

<a name="beanie.odm.queries.update.UpdateQuery"></a>
## UpdateQuery Objects

```python
class UpdateQuery(UpdateMethods,  SessionMethods)
```

Update Query base class

Inherited from:

- [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/`sessionmethods`)
- [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/`aggregatemethods`)

<a name="beanie.odm.queries.update.UpdateQuery.update"></a>
#### update

```python
 | update(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None) -> "UpdateQuery"
```

Provide modifications to the update query. The same as `update()`

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

<a name="beanie.odm.queries.update.UpdateMany"></a>
## UpdateMany Objects

```python
class UpdateMany(UpdateQuery)
```

Update Many query class

Inherited from:

- [UpdateQuery](https://roman-right.github.io/beanie/api/queries/`updatequery`)

<a name="beanie.odm.queries.update.UpdateMany.update_many"></a>
#### update\_many

```python
 | update_many(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None)
```

Provide modifications to the update query

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

<a name="beanie.odm.queries.update.UpdateMany.__await__"></a>
#### \_\_await\_\_

```python
 | __await__() -> UpdateResult
```

Run the query

**Returns**:



<a name="beanie.odm.queries.update.UpdateOne"></a>
## UpdateOne Objects

```python
class UpdateOne(UpdateQuery)
```

Update One query class

Inherited from:

- [UpdateQuery](https://roman-right.github.io/beanie/api/queries/`updatequery`)

<a name="beanie.odm.queries.update.UpdateOne.update_one"></a>
#### update\_one

```python
 | update_one(*args: Union[Dict[str, Any], Mapping[str, Any]], *, session: Optional[ClientSession] = None)
```

Provide modifications to the update query. The same as `update()`

**Arguments**:

- `args`: *Union[dict, Mapping] - the modifications to apply.
- `session`: Optional[ClientSession]

**Returns**:

UpdateMany query

<a name="beanie.odm.queries.update.UpdateOne.__await__"></a>
#### \_\_await\_\_

```python
 | __await__() -> UpdateResult
```

Run the query

**Returns**:



<a name="beanie.odm.queries.delete"></a>
# beanie.odm.queries.delete

<a name="beanie.odm.queries.delete.DeleteQuery"></a>
## DeleteQuery Objects

```python
class DeleteQuery(SessionMethods)
```

Deletion Query

<a name="beanie.odm.queries.delete.DeleteMany"></a>
## DeleteMany Objects

```python
class DeleteMany(DeleteQuery)
```

<a name="beanie.odm.queries.delete.DeleteMany.__await__"></a>
#### \_\_await\_\_

```python
 | __await__() -> DeleteResult
```

Run the query

**Returns**:



<a name="beanie.odm.queries.delete.DeleteOne"></a>
## DeleteOne Objects

```python
class DeleteOne(DeleteQuery)
```

<a name="beanie.odm.queries.delete.DeleteOne.__await__"></a>
#### \_\_await\_\_

```python
 | __await__() -> DeleteResult
```

Run the query

**Returns**:



<a name="beanie.odm.queries.aggregation"></a>
# beanie.odm.queries.aggregation

<a name="beanie.odm.queries.aggregation.AggregationQuery"></a>
## AggregationQuery Objects

```python
class AggregationQuery(BaseCursorQuery,  SessionMethods)
```

Aggregation Query

Inherited from:

- [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/`sessionmethods`) - session methods
- [BaseCursorQuery](https://roman-right.github.io/beanie/api/queries/`basecursorquery`) - async generator

<a name="beanie.odm.queries.cursor"></a>
# beanie.odm.queries.cursor

<a name="beanie.odm.queries.cursor.BaseCursorQuery"></a>
## BaseCursorQuery Objects

```python
class BaseCursorQuery()
```

BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
which parse result with model

<a name="beanie.odm.queries.cursor.BaseCursorQuery.to_list"></a>
#### to\_list

```python
 | async to_list(length: Optional[int] = None) -> Union[List[BaseModel], List[Dict[str, Any]]]
```

Get list of documents

**Arguments**:

- `length`: Optional[int] - length of the list

**Returns**:

Union[List[BaseModel], List[Dict[str, Any]]]

