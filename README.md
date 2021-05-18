[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)](https://github.com/roman-right/beanie)

## Overview

[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python
object-document mapper (ODM) for MongoDB, based
on [Motor](https://motor.readthedocs.io/en/stable/)
and [Pydantic](https://pydantic-docs.helpmanual.io/).

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

## Getting Started

### Document

The `Document` class in Beanie is responsible for mapping and handling the data
from the collection. It is inherited from the `BaseModel` Pydantic class, so it
follows the same data typing and parsing behavior.

Each document has `id` fields of type `PydanticObjectId` which reflects the
unique `_id` field in
MongoDB. [MongoDB doc](https://docs.mongodb.com/manual/reference/glossary/#term-id)

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

More details about Documents, collections, and indexes configuration could be
found in the [documentation](https://roman-right.github.io/beanie/document/).

### Initialization

Beanie uses Motor as an async database engine. To init previously created
documents, you should provide the Motor database instance and list of your
document models to the `init_beanie(...)` function, as it is shown in the
example:

```python
import motor
from beanie import init_beanie


async def init():
    # Crete Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )

    # Init beanie with the Product document class
    await init_beanie(database=client.db_name, document_models=[Product])

```

### Create

Beanie supports and single document creation and batch inserts:

#### Insert one

```python
bar = Product(name="Tony's", price=5.95, category=Category(name="Chocolate"))
await bar.insert()
```

#### Insert many

```python
milka = Product(name="Milka", price=3.05, category=chocolate)
peanut_bar = Product(name="Peanut Bar", price=4.44, category=chocolate)
await Product.insert_many([milka, peanut_bar])
```

Other details and examples could be found in the [documentation](https://roman-right.github.io/beanie/insert/)

### Find

#### Get

The simplest way to get the document is to get it by the `id` field.
Method `get()` is responsible for this:

```python
bar = await Product.get(PydanticObjectId("608da169eb9e17281f0ab2ff"))
```

#### Find One

To get a single document by any other search criteria you can use `find_one()`
method. It responds with awaitable object `FindOne`, which returns `Document`
instance or `None` on `await`

```python
bar = await Product.find_one(
    Product.name == "Peanut Bar",
    Product.category.name == "Chocolate"
)
```

`FindOne` supports projections to grab and return data in needed format only

```python
class ProductShortView(BaseModel):
    name: str
    price: float


bar = await Product.find_one(
    Product.name == "Peanut Bar"
).project(ProductShortView)
```

#### Find Many

To find many documents `find` or `find_many` (which is the same) method could
be used. These methods return the `FindMany` instance, which implements
the `async generator` pattern. It means found documents are available in
the `async for` loop:

```python
async for product in Product.find(
        Product.category.name == "Chocolate"
):
    print(product)
```

The `to_list` method will put all the found documents on the list

```python
products = await Product.find(
    Product.category.name == "Chocolate"
).to_list()
```

`FindMany` supports chain filtering, where you can build your filter query with
many `find` methods

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").find(
    Product.price < 5).to_list()
```

You can sort, skip, limit and project with `FindMany` query too

```python
class ProductShortView(BaseModel):
    name: str
    price: float


products = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 3.5
).sort(-Product.price).limit(10).project(ProductShortView)

```

#### Query Building

And `FindOne` and `FindMany` support native python comparison operators, Beanie
find operators and native PyMongo find query syntax.

**Python comparison operators**

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").find(
    Product.price < 5).to_list()
```

**Beanie Find Operators** are classes - wrappers over MongoDB find operators.

```python
from beanie.operators import In

products = await Product.find(
    In(Product.price, [1, 2, 3, 4, 5])
).to_list()
```

Here you can see `In` operator, which reflects `$in`. The whole list of the
find operators could be
found [here](https://roman-right.github.io/beanie/api/operators/find/)

**Native PyMongo find query syntax**

```python
products = await Product.find(
    {"$in": {"price": [1, 2, 3, 4, 5]}}
).to_list()
```

#### All

To get all the documents `find_all` or `all` methods can be used.

```python
all_products = await Product.all().to_list()
```

Information about sorting, skips, limits, and projections could be found in
the [documentation](https://roman-right.github.io/beanie/find/)

### Update

#### Update Methods

`Document`, `FindMany` and `FindOne`
implement [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#updatemethods)
interface. It supports `update`, `set`, `inc` and `current_date` methods.

#### Document

Implementing `UpdateMethods` interface `Document` instance
creates [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone)
object and provides self id as the search criteria there. Then `UpdateOne`
instance is handling all the update operations.

`update` method is used to update the document data. It supports native Pymongo
syntax and Beanie Update operators.

Native syntax

```python
bar = await Product.find_one(Product.name == "Milka")
await bar.update({"$set": {Product.price: 10}})
```

Update operatos

```python
await bar.update(Set({Product.price: 10}))
```

The whole list of the Beanie update operators can be
found [by link](https://roman-right.github.io/beanie/api/operators/update/)

`inc`, `set` and `current_date` methods are popular update operations preset.
Next example shows how to add `1` to the document's price:

```python
await bar.inc({Product.price: 1})
```

#### Update One

Implementing `UpdateMethods` interface `Document` instance
creates [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone)
object and provides search criteria there. All the update methods work the same
way as for the `Document` instance.

Native syntax

```python
await Product.find_one(
    Product.name == "Milka"
).update({"$set": {Product.price: 10}})
```

Update Operators

```python
await Product.find_one(
    Product.name == "Milka"
).update(Set({Product.price: 10}))
```

Preset Methods

```python
await Product.find_one(
    Product.name == "Milka"
).inc({Product.price: 1})
```

#### Update Many

`FindMany` uses the same patter as `FindOne` but creates `UpdateMany` instance
instead of `UpdateOne` respectively. It supports `UpdateMethods` too.

```python
await Product.find(
    Product.category.name == "Chocolate"
).update({"$set": {Product.price: 100}})
```

More details and examples about update queries could be found in
the [documentation](https://roman-right.github.io/beanie/update/)

### Delete

`delete()` method is supported and by the `Document` instances, and by the `FindOne`
and by the `FindMany` instances. It deletes documents using id or search
criteria respectively.

#### Document

```python
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()
```

#### One

```python
await Product.find_one(Product.name == "Milka").delete()
```

#### Many

```python
await Product.find(
    Product.category.name == "Chocolate"
).delete()
```

#### ALL

```python
await Product.delete_all()
```

More information could be found in the [documentation](https://roman-right.github.io/beanie/delete/)

### Aggregate

You can aggregate and over the whole collection, using `aggregate()` method of the `Document` class, and over search criteria, using `FindMany` instance. 

#### Aggregation Methods

`FindMany` and `Document` classes implements [AggregateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods) interface with preset methods

Example of average calculation:

*With search criteria*
```python
avg_price = await Product.find(
    Product.category.name == "Chocolate"
).avg(Product.price)
```

*Over the whole collection*
```python
avg_price = await Product.avg(Product.price)
```

#### Native syntax

You can use the native PyMongo syntax of the aggregation pipelines to aggregate over the whole collection or over the subset too. `projection_model` parameter is responsible for the output format. It will return dictionaries, if this parameter is not provided.

```python
class OutputItem(BaseModel):
    id: str = Field(None, alias="_id")
    total: int


result = await Product.find(
    Product.category.name == "Chocolate").aggregate(
    [{"$group": {"_id": "$category.name", "total": {"$avg": "$price"}}}],
    projection_model=OutputItem
).to_list()

```

### Documentation

- **[Doc](https://roman-right.github.io/beanie/)** -
  Usage examples with descriptions
- **[API](https://roman-right.github.io/beanie/api/document/)** - Full list of
  the classes and methods

### Example Projects

- **[FastAPI Demo](https://github.com/roman-right/beanie-fastapi-demo)** -
  Beanie and FastAPI collaboration demonstration. CRUD and Aggregation.
- **[Indexes Demo](https://github.com/roman-right/beanie-index-demo)** -
  Regular and Geo Indexes usage example wrapped to a microservice.

### Articles

- **[Announcing Beanie - MongoDB ODM](https://dev.to/romanright/announcing-beanie-mongodb-odm-56e)**
- **[Build a Cocktail API with Beanie and MongoDB](https://developer.mongodb.com/article/beanie-odm-fastapi-cocktails/)**
- **[MongoDB indexes with Beanie](https://dev.to/romanright/mongodb-indexes-with-beanie-43e8)**
- **[Beanie Projections. Reducing network and database load.](https://dev.to/romanright/beanie-projections-reducing-network-and-database-load-3bih)**

### Resources

- **[GitHub](https://github.com/roman-right/beanie)** - GitHub page of the
  project
- **[Changelog](https://roman-right.github.io/beanie/changelog)** - list of all
  the valuable changes
- **[Discord](https://discord.gg/ZTTnM7rMaz)** - ask your questions, share
  ideas or just say `Hello!!`

----
Supported by [JetBrains](https://jb.gg/OpenSource)

[![JetBrains](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/jetbrains.svg)](https://jb.gg/OpenSource)
