[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/white_bg.svg)](https://github.com/roman-right/beanie)

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
## Example

```python
from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie
import asyncio, motor

class Category(BaseModel):
    name: str
    description: str

class Product(Document):
    name: str                          # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(float)              # You can also specify that a field should correspond to an index
    category: Category                 # You can include pydantic models as well

# Beanie is fully asynchronous, so we will access it from an async function
async def example():
    # Beanie uses Motor under the hood 
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://user:pass@host:27017")

    # Init beanie with the Product document class
    await init_beanie(database=client.db_name, document_models=[Product])

    chocolate = Category(name="Chocolate", description="A preparation of roasted and ground cacao seeds.")
    # Beanie documents work just like pydantic models
    tonybar = Product(name="Tony's", price=5.95, category=chocolate)
    # And can be inserted into the database
    await tonybar.insert() 
    
    # You can find documents with pythonic syntax
    product = await Product.find_one(Product.price < 10)
    
    # And update them
    await product.set({Product.name:"Gold bar"})
    
asyncio.run(example())
```

## Links

### Documentation

- **[Doc](https://roman-right.github.io/beanie/)** - Tutorial, API docmentation, and development guidlines.

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
