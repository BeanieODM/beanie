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
    client = Redis(host="192.168.1.11", port=6379, db=0)

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
