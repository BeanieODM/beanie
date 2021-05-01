[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)](https://github.com/roman-right/beanie)

# Getting Started with Beanie

[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python
object-document mapper (ODM) for MongoDB

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
from beanie import Document


class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str
    description: Optional[str] = None
    price: float
    category: Category
```

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
async def create():
    chocolate = Category(name="Chocolate")

    # Single:

    bar = Product(name="Tony's", price=5.95, category=chocolate)
    await bar.insert()

    # Multi

    milka = Product(name="Milka", price=3.05, category=chocolate)
    peanut_bar = Product(name="Peanut Bar", price=4.44, category=chocolate)
    await Product.insert_many([milka, peanut_bar])
```

### Find

```python
async def find():
    # All

    all_products = await Product.all().to_list()

    # Single

    # By id
    bar = await Product.get("608da169eb9e17281f0ab2ff")

    # By name
    bar = await Product.find_one(Product.name == "Peanut Bar")
    
    # Multi

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
```

### Update

```python
async def update():
    # Single 
    await Product.find_one(Product.name == "Milka").set({Product.price: 3.33})

    # Or
    bar = await Product.find_one(Product.name == "Milka")
    await bar.update(Set({Product.price: 3.33}))

    # Or
    bar.price = 3.33
    await bar.replace()

    # Multi
    await Product.find(
        Product.category.name == "Chocolate"
    ).inc({Product.price: 1})
```

----
Supported by [JetBrains](https://jb.gg/OpenSource)

[![JetBrains](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/jetbrains.svg)](https://jb.gg/OpenSource)
