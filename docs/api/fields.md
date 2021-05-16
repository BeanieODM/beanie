## beanie.odm.fields

### Indexed

```python
def Indexed(
	typ, 
	index_type=ASCENDING, 
	**kwargs
)
```

Returns a subclass of `typ` with an extra attribute `_indexed` as a tuple:
- Index 0: `index_type` such as `pymongo.ASCENDING`
- Index 1: `kwargs` passed to `IndexModel`
When instantiated the type of the result will actually be `typ`.

## PydanticObjectId

```python
class PydanticObjectId(ObjectId)
```

Object Id field. Compatible with Pydantic.

## ExpressionField

```python
class ExpressionField(str)
```

### \_\_getattr\_\_

```python
def __getattr__(
	self, 
	item
)
```

Get sub field

**Arguments**:

- `item`: name of the subfield

**Returns**:

ExpressionField

