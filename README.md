# Beanis

## 📢 Work in Progress Disclaimer 📢

**Beanis is currently a work in progress.** While the core functionality is being actively developed, some features may still be in the testing phase. We appreciate your understanding and welcome any feedback or contributions to help us improve the project.

## Overview

[Beanis](https://github.com/andreim14/beanis) is an asynchronous Python object-document mapper (ODM) for Redis, designed to simplify database interactions using data models based on [Pydantic](https://pydantic-docs.helpmanual.io/).

With Beanis, each Redis key is represented by a `Document`, allowing for easy interaction with that key. This includes retrieving, adding, updating, and deleting documents from the key, all while maintaining the simplicity and power of Pydantic models.

Beanis aims to save you time by eliminating boilerplate code, allowing you to focus on the crucial parts of your application.

## Installation

### PIP

```shell
pip install beanis
```

### Poetry

```shell
poetry add beanis
```

## Example

```python
import asyncio
from typing import Optional

from redis import Redis
from pydantic import BaseModel

from beanis import Document, init_beanis


class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str  # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: float
    category: Category  # You can include pydantic models as well


# This is an asynchronous example, so we will access it from an async function
async def example():
    # Beanis uses Redis async client under the hood
    client = Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Initialize beanis with the Product document class
    await init_beanis(database=client, document_models=[Product])

    chocolate = Category(
        name="Chocolate",
        description="A preparation of roasted and ground cacao seeds.",
    )
    # Beanis documents work just like pydantic models
    tonybar = Product(
        id="unique_magic_id", name="Tony's", price=5.95, category=chocolate
    )
    # And can be inserted into the database
    await tonybar.insert()

    # You can find documents by their unique id
    product = await Product.find("unique_magic_id")
    print(product)


if __name__ == "__main__":
    asyncio.run(example())

```

---

Thanks to the amazing team behind [Beanie](https://github.com/BeanieODM/beanie), Beanis brings similar powerful ODM capabilities to Redis, making it easier than ever to manage your Redis database with Python. Please check them out:

[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/white_bg.svg)](https://github.com/BeanieODM/beanie)
