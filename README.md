[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)](https://github.com/roman-right/beanie)

# Getting Started with Beanie

[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python
object-document mapper (ODM) for MongoDB, based on [Motor](https://motor.readthedocs.io/en/stable/) and [Pydantic](https://pydantic-docs.helpmanual.io/).

When using Beanie each database collection has a corresponding `Document` that
is used to interact with that collection. In addition to retrieving data,
Beanie allows you to add, update, or delete documents from the collection as
well.

Beanie saves you time by removing boiler-plate code and it helps you focus on
the parts of your app that actually matter.

Data and schema migrations are supported by Beanie out of the box.

## Installation

### PIP

```shell
pip install beanie
```

### Poetry

```shell
poetry add beanie
```

## Basic Example

### Document models

```python
from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed


class Category(BaseModel):
    name: str
    description: str


class Product(Document):  # This is the model
    name: str
    description: Optional[str] = None
    price: Indexed(float)
    category: Category

    class Collection:
        name = "products"
```
Each document by default has `id` ObjectId field, which reflects `_id` MongoDB document field. It can be used later as an argument for the `get()` method.

More details about Documents, collections, and indexes configuration could be found in the [tutorial](/tutorial/install/).

### Initialization

```python
import motor
from beanie import init_beanie


async def init():
    # Crete Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )

    # Init beanie with the Note document class
    await init_beanie(database=client.db_name, document_models=[Product])

```

### Create

```python
chocolate = Category(name="Chocolate")

# Single:

bar = Product(name="Tony's", price=5.95, category=chocolate)
await bar.insert()

# Many

milka = Product(name="Milka", price=3.05, category=chocolate)
peanut_bar = Product(name="Peanut Bar", price=4.44, category=chocolate)
await Product.insert_many([milka, peanut_bar])
```

Other details and examples could be found in the [tutorial](/tutorial/insert/)

### Find

```python
# Single

# By id
bar = await Product.get("608da169eb9e17281f0ab2ff")

# By name
bar = await Product.find_one(Product.name == "Peanut Bar")

# Many

# By category

chocolates = await Product.find(
    Product.category.name == "Chocolate"
).to_list()

# And by price

chocolates = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 5
).to_list()

# OR

chocolates = await Product.find(
    Product.category.name == "Chocolate").find(
    Product.price < 5).to_list()

# Complex example:

class ProductShortView(BaseModel):
    name: str
    price: float


products = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 3.5
).sort(-Product.price).limit(10).project(ProductShortView)

# All

all_products = await Product.all().to_list()
```

Information about sorting, skips, limits, and projections could be found in the [tutorial](/tutorial/find/)

### Update

```python
# Single 
await Product.find_one(Product.name == "Milka").set({Product.price: 3.33})

# Or
bar = await Product.find_one(Product.name == "Milka")
await bar.update(Set({Product.price: 3.33}))

# Or
bar.price = 3.33
await bar.replace()

# Many
await Product.find(
    Product.category.name == "Chocolate"
).inc({Product.price: 1})
```

More details and examples about update queries could be found in the [tutorial](/tutorial/update/)

### Delete

```python
# Single 
await Product.find_one(Product.name == "Milka").delete()

# Or
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()

# Many
await Product.find(
    Product.category.name == "Chocolate"
).delete()
```

More information could be found in the [tutorial](/tutorial/delete/)

### Aggregate

```python
# With preset methods

avg_price = await Product.find(
    Product.category.name == "Chocolate"
).avg(Product.price)

# Or without find query

avg_price = await Product.avg(Product.price)

# Native syntax 

class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int
    
result = await Product.find(
    Product.category.name == "Chocolate").aggregate(
    [{"$group": {"_id": "$category.name", "total": {"$avg": "$price"}}}],
    projection_model=OutputItem
).to_list()

```

Information about aggregation preset aggregation methods and native syntax aggregations could be found in the [tutorial](/tutorial/aggregate/)

### Documentation

- **[Tutorial](https://roman-right.github.io/beanie/tutorial/install/)** - Usage examples with descriptions
- **[API](https://roman-right.github.io/beanie/api/document/)** - Full list of the classes and
  methods

### Example Projects

- **[FastAPI Demo](https://github.com/roman-right/beanie-fastapi-demo)** - Beanie and FastAPI collaboration demonstration. CRUD and Aggregation.
- **[Indexes Demo](https://github.com/roman-right/beanie-index-demo)** - Regular and Geo Indexes usage example wrapped to a microservice. 

### Articles

- **[Announcing Beanie - MongoDB ODM](https://dev.to/romanright/announcing-beanie-mongodb-odm-56e)**
- **[Build a Cocktail API with Beanie and MongoDB](https://developer.mongodb.com/article/beanie-odm-fastapi-cocktails/)**
- **[MongoDB indexes with Beanie](https://dev.to/romanright/mongodb-indexes-with-beanie-43e8)**
- **[Beanie Projections. Reducing network and database load.](https://dev.to/romanright/beanie-projections-reducing-network-and-database-load-3bih)**

### Resources

- **[GitHub](https://github.com/roman-right/beanie)** - GitHub page of the project
- **[Changelog](https://roman-right.github.io/beanie/changelog)** - list of all the valuable changes
- **[Discord](https://discord.gg/ZTTnM7rMaz)** - ask your questions, share ideas or just say `Hello!!`


----
Supported by [JetBrains](https://jb.gg/OpenSource)

[![JetBrains](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/jetbrains.svg)](https://jb.gg/OpenSource)
