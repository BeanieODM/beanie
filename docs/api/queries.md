## beanie.odm.queries.find

## FindQuery

```python
class FindQuery(UpdateMethods,  SessionMethods)
```

Find Query base class

## FindMany

```python
class FindMany(BaseCursorQuery,  FindQuery,  AggregateMethods)
```

Find Many query class

It is async generator. Use `async for` or
`to_list` method to work with this

## FindOne

```python
class FindOne(FindQuery)
```

Find One query class

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

