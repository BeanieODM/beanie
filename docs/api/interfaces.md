<a name="beanie.odm.interfaces.update"></a>
# beanie.odm.interfaces.update

<a name="beanie.odm.interfaces.update.UpdateMethods"></a>
## UpdateMethods Objects

```python
class UpdateMethods()
```

Update methods

<a name="beanie.odm.interfaces.update.UpdateMethods.set"></a>
#### set

```python
 | set(expression: Dict[Union[ExpressionField, str], Any], session: Optional[ClientSession] = None)
```

Set values

Example:

```python

class Sample(Document):
    one: int

await Document.find(Sample.one == 1).set({Sample.one: 100})

```

Uses [Set operator](https://roman-right.github.io/beanie/api/operators/update/`set`)

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any] - keys and
values to set
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

<a name="beanie.odm.interfaces.update.UpdateMethods.current_date"></a>
#### current\_date

```python
 | current_date(expression: Dict[Union[ExpressionField, str], Any], session: Optional[ClientSession] = None)
```

Set current date

Uses [CurrentDate operator](https://roman-right.github.io/beanie/api/operators/update/`currentdate`)

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

<a name="beanie.odm.interfaces.update.UpdateMethods.inc"></a>
#### inc

```python
 | inc(expression: Dict[Union[ExpressionField, str], Any], session: Optional[ClientSession] = None)
```

Increment

Example:

```python

class Sample(Document):
    one: int

await Document.find(Sample.one == 1).inc({Sample.one: 100})

```

Uses [Inc operator](https://roman-right.github.io/beanie/api/operators/update/`inc`)

**Arguments**:

- `expression`: Dict[Union[ExpressionField, str], Any]
- `session`: Optional[ClientSession] - pymongo session

**Returns**:

self

<a name="beanie.odm.interfaces.aggregate"></a>
# beanie.odm.interfaces.aggregate

<a name="beanie.odm.interfaces.aggregate.AggregateMethods"></a>
## AggregateMethods Objects

```python
class AggregateMethods()
```

Aggregate methods

<a name="beanie.odm.interfaces.aggregate.AggregateMethods.sum"></a>
#### sum

```python
 | async sum(field: Union[str, ExpressionField], session: Optional[ClientSession] = None) -> float
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

<a name="beanie.odm.interfaces.aggregate.AggregateMethods.avg"></a>
#### avg

```python
 | async avg(field, session: Optional[ClientSession] = None) -> float
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

<a name="beanie.odm.interfaces.aggregate.AggregateMethods.max"></a>
#### max

```python
 | async max(field: Union[str, ExpressionField], session: Optional[ClientSession] = None) -> Any
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

<a name="beanie.odm.interfaces.aggregate.AggregateMethods.min"></a>
#### min

```python
 | async min(field: Union[str, ExpressionField], session: Optional[ClientSession] = None) -> Any
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

<a name="beanie.odm.interfaces.session"></a>
# beanie.odm.interfaces.session

<a name="beanie.odm.interfaces.session.SessionMethods"></a>
## SessionMethods Objects

```python
class SessionMethods()
```

Session methods

<a name="beanie.odm.interfaces.session.SessionMethods.set_session"></a>
#### set\_session

```python
 | set_session(session: Optional[ClientSession] = None)
```

Set pymongo session

**Arguments**:

- `session`: Optional[ClientSession] - pymongo session

**Returns**:



