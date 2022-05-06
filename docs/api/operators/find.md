<a name="beanie.odm.operators.find.comparison"></a>
# beanie.odm.operators.find.comparison

<a name="beanie.odm.operators.find.comparison.Eq"></a>
## Eq Objects

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

<a name="beanie.odm.operators.find.comparison.GT"></a>
## GT Objects

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

<a name="beanie.odm.operators.find.comparison.GTE"></a>
## GTE Objects

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

<a name="beanie.odm.operators.find.comparison.In"></a>
## In Objects

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

<a name="beanie.odm.operators.find.comparison.NotIn"></a>
## NotIn Objects

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

<a name="beanie.odm.operators.find.comparison.LT"></a>
## LT Objects

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

<a name="beanie.odm.operators.find.comparison.LTE"></a>
## LTE Objects

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

<a name="beanie.odm.operators.find.comparison.NE"></a>
## NE Objects

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

<a name="beanie.odm.operators.find.logical"></a>
# beanie.odm.operators.find.logical

<a name="beanie.odm.operators.find.logical.Or"></a>
## Or Objects

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

<a name="beanie.odm.operators.find.logical.And"></a>
## And Objects

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

<a name="beanie.odm.operators.find.logical.Nor"></a>
## Nor Objects

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

<a name="beanie.odm.operators.find.logical.Not"></a>
## Not Objects

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

<a name="beanie.odm.operators.find.element"></a>
# beanie.odm.operators.find.element

<a name="beanie.odm.operators.find.element.Exists"></a>
## Exists Objects

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

<a name="beanie.odm.operators.find.element.Type"></a>
## Type Objects

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

<a name="beanie.odm.operators.find.evaluation"></a>
# beanie.odm.operators.find.evaluation

<a name="beanie.odm.operators.find.evaluation.Expr"></a>
## Expr Objects

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

<a name="beanie.odm.operators.find.evaluation.JsonSchema"></a>
## JsonSchema Objects

```python
class JsonSchema(BaseFindEvaluationOperator)
```

`$jsonSchema` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/>

<a name="beanie.odm.operators.find.evaluation.Mod"></a>
## Mod Objects

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

<a name="beanie.odm.operators.find.evaluation.RegEx"></a>
## RegEx Objects

```python
class RegEx(BaseFindEvaluationOperator)
```

`$regex` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/regex/>

<a name="beanie.odm.operators.find.evaluation.Text"></a>
## Text Objects

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

<a name="beanie.odm.operators.find.evaluation.Text.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(search: str, language: Optional[str] = None, case_sensitive: bool = False, diacritic_sensitive: bool = False)
```

**Arguments**:

- `search`: str
- `language`: Optional[str] = None
- `case_sensitive`: bool = False
- `diacritic_sensitive`: bool = False

<a name="beanie.odm.operators.find.evaluation.Where"></a>
## Where Objects

```python
class Where(BaseFindEvaluationOperator)
```

`$where` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/where/>

<a name="beanie.odm.operators.find.geospatial"></a>
# beanie.odm.operators.find.geospatial

<a name="beanie.odm.operators.find.geospatial.GeoIntersects"></a>
## GeoIntersects Objects

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

    class Settings:
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

<a name="beanie.odm.operators.find.geospatial.GeoWithin"></a>
## GeoWithin Objects

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

    class Settings:
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

<a name="beanie.odm.operators.find.geospatial.Near"></a>
## Near Objects

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

    class Settings:
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

<a name="beanie.odm.operators.find.geospatial.NearSphere"></a>
## NearSphere Objects

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

    class Settings:
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

<a name="beanie.odm.operators.find.array"></a>
# beanie.odm.operators.find.array

<a name="beanie.odm.operators.find.array.All"></a>
## All Objects

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

<a name="beanie.odm.operators.find.array.ElemMatch"></a>
## ElemMatch Objects

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

<a name="beanie.odm.operators.find.array.Size"></a>
## Size Objects

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

<a name="beanie.odm.operators.find.bitwise"></a>
# beanie.odm.operators.find.bitwise

<a name="beanie.odm.operators.find.bitwise.BitsAllClear"></a>
## BitsAllClear Objects

```python
class BitsAllClear(BaseFindBitwiseOperator)
```

`$bitsAllClear` query operator

MongoDB doc:
<https://docs.mongodb.com/manual/reference/operator/query/bitsAllClear/>

<a name="beanie.odm.operators.find.bitwise.BitsAllSet"></a>
## BitsAllSet Objects

```python
class BitsAllSet(BaseFindBitwiseOperator)
```

`$bitsAllSet` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAllSet/

<a name="beanie.odm.operators.find.bitwise.BitsAnyClear"></a>
## BitsAnyClear Objects

```python
class BitsAnyClear(BaseFindBitwiseOperator)
```

`$bitsAnyClear` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAnyClear/

<a name="beanie.odm.operators.find.bitwise.BitsAnySet"></a>
## BitsAnySet Objects

```python
class BitsAnySet(BaseFindBitwiseOperator)
```

`$bitsAnySet` query operator

MongoDB doc:
https://docs.mongodb.com/manual/reference/operator/query/bitsAnySet/

