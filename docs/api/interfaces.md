## beanie.odm.interfaces.update

## UpdateMethods

```python
class UpdateMethods()
```

Update methods

### set

```python
def set(
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Set values

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/update/set/

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any] - keys and
values to set
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

### current\_date

```python
def current_date(
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Set current date

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/update/currentDate/

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

### inc

```python
def inc(
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Increment

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/update/inc/

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

## beanie.odm.interfaces.aggregate

## AggregateMethods

```python
class AggregateMethods()
```

Aggregate methods

### sum

```python
async def sum(
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> float
```

Sum of values of the given field

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - sum

### avg

```python
async def avg(
	field, 
	session: Optional[ClientSession] = None
) -> float
```

Average of values of the given field

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - avg

### max

```python
async def max(
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> Any
```

Max of the values of the given field

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - max

### min

```python
async def min(
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> Any
```

Min of the values of the given field

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - max

## beanie.odm.interfaces.session

## SessionMethods

```python
class SessionMethods()
```

Session methods

### set\_session

```python
def set_session(
	session: Optional[ClientSession] = None
)
```

Set pymongo session

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session

**Returns**:



