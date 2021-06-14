<a name="beanie.odm.fields"></a>
# beanie.odm.fields

<a name="beanie.odm.fields.Indexed"></a>
#### Indexed

```python
Indexed(typ, index_type=ASCENDING, **kwargs)
```

Returns a subclass of `typ` with an extra attribute `_indexed` as a tuple:
- Index 0: `index_type` such as `pymongo.ASCENDING`
- Index 1: `kwargs` passed to `IndexModel`
When instantiated the type of the result will actually be `typ`.

<a name="beanie.odm.fields.PydanticObjectId"></a>
## PydanticObjectId Objects

```python
class PydanticObjectId(ObjectId)
```

Object Id field. Compatible with Pydantic.

<a name="beanie.odm.fields.ExpressionField"></a>
## ExpressionField Objects

```python
class ExpressionField(str)
```

<a name="beanie.odm.fields.ExpressionField.__getattr__"></a>
#### \_\_getattr\_\_

```python
 | __getattr__(item)
```

Get sub field

**Arguments**:

- `item`: name of the subfield

**Returns**:

ExpressionField

