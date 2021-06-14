<a name="beanie.odm.operators.update.general"></a>
# beanie.odm.operators.update.general

<a name="beanie.odm.operators.update.general.Set"></a>
## Set Objects

```python
class Set(BaseUpdateGeneralOperator)
```

`$set` update query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Set({Sample.one, 2})
```
  
  Will return query object like
  
```python
{"$set": {"one": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/set/>

<a name="beanie.odm.operators.update.general.CurrentDate"></a>
## CurrentDate Objects

```python
class CurrentDate(BaseUpdateGeneralOperator)
```

`$currentDate` update query operator

**Example**:

  
```python
class Sample(Document):
    ts: datetime

CurrentDate({Sample.ts, True})
```
  
  Will return query object like
  
```python
{"$currentDate": {"ts": True}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/currentDate/>

<a name="beanie.odm.operators.update.general.Inc"></a>
## Inc Objects

```python
class Inc(BaseUpdateGeneralOperator)
```

`$inc` update query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Inc({Sample.one, 2})
```
  
  Will return query object like
  
```python
{"$inc": {"one": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/inc/>

<a name="beanie.odm.operators.update.general.Min"></a>
## Min Objects

```python
class Min(BaseUpdateGeneralOperator)
```

`$min` update query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Min({Sample.one, 2})
```
  
  Will return query object like
  
```python
{"$min": {"one": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/min/>

<a name="beanie.odm.operators.update.general.Max"></a>
## Max Objects

```python
class Max(BaseUpdateGeneralOperator)
```

`$max` update query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Max({Sample.one, 2})
```
  
  Will return query object like
  
```python
{"$max": {"one": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/max/>

<a name="beanie.odm.operators.update.general.Mul"></a>
## Mul Objects

```python
class Mul(BaseUpdateGeneralOperator)
```

`$mul` update query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Mul({Sample.one, 2})
```
  
  Will return query object like
  
```python
{"$mul": {"one": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/update/mul/>

<a name="beanie.odm.operators.update.general.Rename"></a>
## Rename Objects

```python
class Rename(BaseUpdateGeneralOperator)
```

`$rename` update query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/update/rename/>

<a name="beanie.odm.operators.update.general.SetOnInsert"></a>
## SetOnInsert Objects

```python
class SetOnInsert(BaseUpdateGeneralOperator)
```

`$setOnInsert` update query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/update/setOnInsert/>

<a name="beanie.odm.operators.update.general.Unset"></a>
## Unset Objects

```python
class Unset(BaseUpdateGeneralOperator)
```

`$unset` update query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/update/unset/>

<a name="beanie.odm.operators.update.array"></a>
# beanie.odm.operators.update.array

<a name="beanie.odm.operators.update.array.AddToSet"></a>
## AddToSet Objects

```python
class AddToSet(BaseUpdateArrayOperator)
```

`$addToSet` update array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

AddToSet({Sample.results, 2})
```
  
  Will return query object like
  
```python
{"$addToSet": {"results": 2}}
```
  
  MongoDB docs:
  <https://docs.mongodb.com/manual/reference/operator/update/addToSet/>

<a name="beanie.odm.operators.update.array.Pop"></a>
## Pop Objects

```python
class Pop(BaseUpdateArrayOperator)
```

`$pop` update array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

Pop({Sample.results, 2})
```
  
  Will return query object like
  
```python
{"$pop": {"results": -1}}
```
  
  MongoDB docs:
  <https://docs.mongodb.com/manual/reference/operator/update/pop/>

<a name="beanie.odm.operators.update.array.Pull"></a>
## Pull Objects

```python
class Pull(BaseUpdateArrayOperator)
```

`$pull` update array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

Pull(In(Sample.result, [1,2,3,4,5])
```
  
  Will return query object like
  
```python
{"$pull": { "results": { $in: [1,2,3,4,5] }}}
```
  
  MongoDB docs:
  <https://docs.mongodb.com/manual/reference/operator/update/pull/>

<a name="beanie.odm.operators.update.array.Push"></a>
## Push Objects

```python
class Push(BaseUpdateArrayOperator)
```

`$push` update array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

Push({Sample.results: 1})
```
  
  Will return query object like
  
```python
{"$push": { "results": 1}}
```
  
  MongoDB docs:
  <https://docs.mongodb.com/manual/reference/operator/update/push/>

<a name="beanie.odm.operators.update.array.PullAll"></a>
## PullAll Objects

```python
class PullAll(BaseUpdateArrayOperator)
```

`$pullAll` update array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

PullAll({ Sample.results: [ 0, 5 ] })
```
  
  Will return query object like
  
```python
{"$pullAll": { "results": [ 0, 5 ] }}
```
  
  MongoDB docs:
  <https://docs.mongodb.com/manual/reference/operator/update/pullAll/>

<a name="beanie.odm.operators.update.bitwise"></a>
# beanie.odm.operators.update.bitwise

<a name="beanie.odm.operators.update.bitwise.Bit"></a>
## Bit Objects

```python
class Bit(BaseUpdateBitwiseOperator)
```

`$bit` update query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/update/bit/>

