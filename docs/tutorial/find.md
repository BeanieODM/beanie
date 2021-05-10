# Find documents

Beanie provides two ways to find documents:

- Find One document
- Find Many documents

On searching for a single document it uses [FindOne](/beanie/api/queries/#findone)
query, many documents - [FindMany](/beanie/api/queries/#findmany) query.

Next document models will be used for this tutorial:

```python
from typing import Optional
from pydantic import BaseModel
from beanie import Document


class Category(BaseModel):
    name: str
    description: str


class Product(Document):  # This is the model
    name: str
    description: Optional[str] = None
    price: float
    category: Category

    class Collection:
        name = "products"


class ProductShortView(BaseModel):
    name: str
    price: float

```

## Search Criteria

As search criteria, Beanie supports python comparison methods, wrappers over
find query operators, and native syntax.

Python comparison operators must be used with the class fields (and nested
fields)

```python
products = await Product.find(Product.price < 10)
```

Supported operators: `==`, `>`, `>=`, `<`, `<=`, `!=`

Most of the query operators have wrappers.

For example `$in` operator:

```python
products = await Product.find(
    In(Product.category.name, ["Chocolate", "Fruits"]))
```

The whole list of the find query operators could be
found [here](/beanie/api/operators/find/)

For the complex cases native PyMongo syntax is also supported:

```python
products = await Product.find({"price": 1000})
```

## Find One

To get the document by id it uses [get](/beanie/api/document/#get) method.

```python
bar = await Product.get("608da169eb9e17281f0ab2ff")
```

To find document by searching criteria it
uses [find_one](/beanie/api/document/#find_one) method

```python
bar = await Product.find_one(Product.name == "Peanut Bar")
```

Projection could be used to return the document in another model format

```python
bar = await Product.find_one(Product.name == "Peanut Bar",
                             projection_model="ProductShortView")
```

## Find Many

To find many documents it uses [find_many](/beanie/api/document/#find_many) (
or [find](/beanie/api/document/#find), which is the same ) method

### Cursor

It will return the [FindMany](/beanie/api/queries/#findmany) query object. It
implements an async generator pattern. Found documents are available
via `async for` loop:

```python
async for product in Product.find_many(
        Product.category.name == "Chocolate"
):
    print(product)
```

[to_list](/beanie/api/queries/#to_list) method could be used to return the list of the
found documents

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate"
).to_list()
```

### List of the search criterias

Search criterias could be listed as *args parameters of the `find*` method:

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 5
).to_list()
```

### Chaining

Or a chain of `find` methods could be used instead

```python
chocolates = (await Product
              .find(Product.category.name == "Chocolate")
              .find(Product.price < 5).to_list()
              )
```

### Sorting

Sorting could be set up with the [sort](/beanie/api/queries/#sort) method.

It supports arguments like `+` or `-` class fields

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort(-Product.price).to_list()
```

strings:

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort("-price").to_list()
```

and lists of tuples:

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort(
    [
        (Product.price, pymongo.DESCENDING),
        (Product.name, pymongo.ASCENDING),
    ]
).to_list()
```

### Skip and limit

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").skip(2).to_list()

chocolates = await Product.find(
    Product.category.name == "Chocolate").limit(2).to_list()
```

### Projections

Projection could be used to return the documents in another model format

```python

chocolates = await Product.find(
    Product.category.name == "Chocolate").project(ProductShortView).to_list()
```

Inner Settings class can be used to make a custom projection

```python
class ProductView(BaseModel):
    name: str
    category: str

    class Settings:
        projection = {"name": 1, "category": "$category.name"}


chocolates = await Product.find(
    Product.category.name == "Chocolate").project(ProductView).to_list()
```