## beanie.odm.operators.find.comparison

## Eq

```python
class Eq(BaseFindComparisonOperator)
```

`equal` query operator

**Example**:

  
```python
class Product(Document):
    price: float

Eq(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": 2}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/eq/>

## GT

```python
class GT(BaseFindComparisonOperator)
```

`$gt` query operator

**Example**:

  
```python
class Product(Document):
    price: float

GT(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": {"$gt": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/gt/>

## GTE

```python
class GTE(BaseFindComparisonOperator)
```

`$gte` query operator

**Example**:

  
```python
class Product(Document):
    price: float

GTE(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": {"$gte": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/gte/>

## In

```python
class In(BaseFindComparisonOperator)
```

`$in` query operator

**Example**:

  
```python
class Product(Document):
    price: float

In(Product.price, [2, 3, 4])
```
  
  Will return query object like
  
```python
{"price": {"$in": [2, 3, 4]}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/in/>

## NotIn

```python
class NotIn(BaseFindComparisonOperator)
```

`$nin` query operator

**Example**:

  
```python
class Product(Document):
    price: float

NotIn(Product.price, [2, 3, 4])
```
  
  Will return query object like
  
```python
{"price": {"$nin": [2, 3, 4]}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/nin/>

## LT

```python
class LT(BaseFindComparisonOperator)
```

`$lt` query operator

**Example**:

  
```python
class Product(Document):
    price: float

LT(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": {"$lt": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/lt/>

## LTE

```python
class LTE(BaseFindComparisonOperator)
```

`$lte` query operator

**Example**:

  
```python
class Product(Document):
    price: float

LTE(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": {"$lte": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/lte/>

## NE

```python
class NE(BaseFindComparisonOperator)
```

`$ne` query operator

**Example**:

  
```python
class Product(Document):
    price: float

NE(Product.price, 2)
```
  
  Will return query object like
  
```python
{"price": {"$ne": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/ne/>

## beanie.odm.operators.find.logical

## Or

```python
class Or(LogicalOperatorForListOfExpressions)
```

`$or` query operator

**Example**:

  
```python
class Product(Document):
    price: float
    category: str

Or({Product.price<10}, {Product.category=="Sweets"})
```
  
  Will return query object like
  
```python
{"$or": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/or/>

## And

```python
class And(LogicalOperatorForListOfExpressions)
```

`$and` query operator

**Example**:

  
```python
class Product(Document):
    price: float
    category: str

And({Product.price<10}, {Product.category=="Sweets"})
```
  
  Will return query object like
  
```python
{"$and": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/and/>

## Nor

```python
class Nor(BaseFindLogicalOperator)
```

`$nor` query operator

**Example**:

  
```python
class Product(Document):
    price: float
    category: str

Nor({Product.price<10}, {Product.category=="Sweets"})
```
  
  Will return query object like
  
```python
{"$nor": [{"price": {"$lt": 10}}, {"category": "Sweets"}]}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/nor/>

## Not

```python
class Not(BaseFindLogicalOperator)
```

`$not` query operator

**Example**:

  
```python
class Product(Document):
    price: float
    category: str

Not({Product.price<10})
```
  
  Will return query object like
  
```python
{"$not": {"price": {"$lt": 10}}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/not/>

## beanie.odm.operators.find.element

## Exists

```python
class Exists(BaseFindElementOperator)
```

`$exists` query operator

**Example**:

  
```python
class Product(Document):
    price: float

Exists(Product.price, True)
```
  
  Will return query object like
  
```python
{"price": {"$exists": True}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/exists/>

## Type

```python
class Type(BaseFindElementOperator)
```

`$type` query operator

**Example**:

  
```python
class Product(Document):
    price: float

Type(Product.price, "decimal")
```
  
  Will return query object like
  
```python
{"price": {"$type": "decimal"}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/type/>

## beanie.odm.operators.find.evaluation

## Expr

```python
class Expr(BaseFindEvaluationOperator)
```

`$type` query operator

**Example**:

  
```python
class Sample(Document):
    one: int
    two: int

Expr({"$gt": [ "$one" , "$two" ]})
```
  
  Will return query object like
  
```python
{"$expr": {"$gt": [ "$one" , "$two" ]}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/expr/>

## JsonSchema

```python
class JsonSchema(BaseFindEvaluationOperator)
```

`$jsonSchema` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/>

## Mod

```python
class Mod(BaseFindEvaluationOperator)
```

`$mod` query operator

**Example**:

  
```python
class Sample(Document):
    one: int

Mod(Sample.one, 4, 0)
```
  
  Will return query object like
  
```python
{ "one": { "$mod": [ 4, 0 ] } }
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/mod/>

## RegEx

```python
class RegEx(BaseFindEvaluationOperator)
```

`$regex` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/regex/>

## Text

```python
class Text(BaseFindEvaluationOperator)
```

`$text` query operator

**Example**:

  
```python
class Sample(Document):
    description: Indexed(str, pymongo.TEXT)

Text("coffee")
```
  
  Will return query object like
  
```python
{
    "$text": {
        "$search": "coffee" ,
        "$caseSensitive": False,
        "$diacriticSensitive": False
    }
}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/text/>

### \_\_init\_\_

```python
def __init__(
	self, 
	search: str, 
	language: Optional[str] = None, 
	case_sensitive: bool = False, 
	diacritic_sensitive: bool = False
)
```

**Arguments**:

- `search`: str
- `language`: Optional[str] = None
- `case_sensitive`: bool = False
- `diacritic_sensitive`: bool = False

## Where

```python
class Where(BaseFindEvaluationOperator)
```

`$where` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/where/>

## beanie.odm.operators.find.geospatial

## GeoIntersects

```python
class GeoIntersects(BaseFindGeospatialOperator)
```

`$geoIntersects` query operator

**Example**:

  
```python
class GeoObject(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]

class Place(Document):
    geo: GeoObject

    class Collection:
        name = "places"
        indexes = [
            [("geo", pymongo.GEOSPHERE)],  # GEO index
        ]

GeoIntersects(Place.geo, "Polygon", [[0,0], [1,1], [3,3]])
```
  
  Will return query object like
  
```python
{
    "geo": {
        "$geoIntersects": {
            "$geometry": {
                "type": "Polygon",
                "coordinates": [[0,0], [1,1], [3,3]],
            }
        }
    }
}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/geoIntersects/>

## GeoWithin

```python
class GeoWithin(BaseFindGeospatialOperator)
```

`$geoWithin` query operator

**Example**:

  
```python
class GeoObject(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]

class Place(Document):
    geo: GeoObject

    class Collection:
        name = "places"
        indexes = [
            [("geo", pymongo.GEOSPHERE)],  # GEO index
        ]

GeoWithin(Place.geo, "Polygon", [[0,0], [1,1], [3,3]])
```
  
  Will return query object like
  
```python
{
    "geo": {
        "$geoWithin": {
            "$geometry": {
                "type": "Polygon",
                "coordinates": [[0,0], [1,1], [3,3]],
            }
        }
    }
}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/geoWithin/>

## Near

```python
class Near(BaseFindGeospatialOperator)
```

`$near` query operator

**Example**:

  
```python
class GeoObject(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]

class Place(Document):
    geo: GeoObject

    class Collection:
        name = "places"
        indexes = [
            [("geo", pymongo.GEOSPHERE)],  # GEO index
        ]

Near(Place.geo, 1.2345, 2.3456, min_distance=500)
```
  
  Will return query object like
  
```python
{
    "geo": {
        "$near": {
            "$geometry": {
                "type": "Point",
                "coordinates": [1.2345, 2.3456],
            },
            "$maxDistance": 500,
        }
    }
}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/near/>

## NearSphere

```python
class NearSphere(Near)
```

`$nearSphere` query operator

**Example**:

  
```python
class GeoObject(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]

class Place(Document):
    geo: GeoObject

    class Collection:
        name = "places"
        indexes = [
            [("geo", pymongo.GEOSPHERE)],  # GEO index
        ]

NearSphere(Place.geo, 1.2345, 2.3456, min_distance=500)
```
  
  Will return query object like
  
```python
{
    "geo": {
        "$nearSphere": {
            "$geometry": {
                "type": "Point",
                "coordinates": [1.2345, 2.3456],
            },
            "$maxDistance": 500,
        }
    }
}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/nearSphere/>

## beanie.odm.operators.find.array

## All

```python
class All(BaseFindArrayOperator)
```

`$all` array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

All(Sample.results, [80, 85])
```
  
  Will return query object like
  
```python
{"results": {"$all": [80, 85]}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/all>

## ElemMatch

```python
class ElemMatch(BaseFindArrayOperator)
```

`$elemMatch` array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

ElemMatch(Sample.results, [80, 85])
```
  
  Will return query object like
  
```python
{"results": {"$elemMatch": [80, 85]}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/elemMatch/>

## Size

```python
class Size(BaseFindArrayOperator)
```

`$size` array query operator

**Example**:

  
```python
class Sample(Document):
    results: List[int]

Size(Sample.results, 2)
```
  
  Will return query object like
  
```python
{"results": {"$size": 2}}
```
  
  MongoDB doc:
  <https://docs.mongodb.com/manual/reference/operator/query/size/>

## beanie.odm.operators.find.bitwise

## BitsAllClear

```python
class BitsAllClear(BaseFindBitwiseOperator)
```

`$bitsAllClear` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/bitsAllClear/>

## BitsAllSet

```python
class BitsAllSet(BaseFindBitwiseOperator)
```

`$bitsAllSet` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAllSet/

## BitsAnyClear

```python
class BitsAnyClear(BaseFindBitwiseOperator)
```

`$bitsAnyClear` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAnyClear/

## BitsAnySet

```python
class BitsAnySet(BaseFindBitwiseOperator)
```

`$bitsAnySet` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAnySet/

