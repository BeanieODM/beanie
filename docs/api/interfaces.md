## beanie.odm.interfaces.update

## UpdateMethods

```python
class UpdateMethods()
```

Update methods

### set

```python
def set(
	self, 
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Set values

Example:

```python

class Sample(Document):
    one: int

await Document.find(Sample.one == 1).set({Sample.one: 100})

```

Uses [Set operator](/beanie/api/operators/update/#set)

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any] - keys and
values to set
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

### current\_date

```python
def current_date(
	self, 
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Set current date

Uses [CurrentDate operator](/beanie/api/operators/update/#currentdate)

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

### inc

```python
def inc(
	self, 
	expression: Dict[Union[ExpressionField, str], Any], 
	session: Optional[ClientSession] = None
)
```

Increment

Example:

```python

class Sample(Document):
    one: int

await Document.find(Sample.one == 1).inc({Sample.one: 100})

```

Uses [Inc operator](/beanie/api/operators/update/#inc)

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
	self, 
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> float
```

Sum of values of the given field

Example:

```python

class Sample(Document):
    price: int
    count: int

sum_count = await Document.find(Sample.price <= 100).sum(Sample.count)

```

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - sum

### avg

```python
async def avg(
	self, 
	field, 
	session: Optional[ClientSession] = None
) -> float
```

Average of values of the given field

Example:

```python

class Sample(Document):
    price: int
    count: int

avg_count = await Document.find(Sample.price <= 100).avg(Sample.count)
```

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - avg

### max

```python
async def max(
	self, 
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> Any
```

Max of the values of the given field

Example:

```python

class Sample(Document):
    price: int
    count: int

max_count = await Document.find(Sample.price <= 100).max(Sample.count)
```

**Arguments**:

- `field`: Union[str, ExpressionField]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

float - max

### min

```python
async def min(
	self, 
	field: Union[str, ExpressionField], 
	session: Optional[ClientSession] = None
) -> Any
```

Min of the values of the given field

Example:

```python

class Sample(Document):
    price: int
    count: int

min_count = await Document.find(Sample.price <= 100).min(Sample.count)
```

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
	self, 
	session: Optional[ClientSession] = None
)
```

Set pymongo session

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session

**Returns**:



