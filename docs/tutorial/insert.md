# Insert the documents


Beanie documents behave just like pydantic models (because they are pydantic models).
Hence a document can be created in a similar fashion to pydantic:
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

    class Settings:
        name = "products"
        
chocolate = Category(name="Chocolate", description="A preparation of roasted and ground cacao seeds.")
tonybar = Product(name="Tony's", price=5.95, category=chocolate)
marsbar = Product(name="Mars", price=1, category=chocolate)
```
This however does not save the documents to the database yet.

## Insert a single document
To insert a document into the database, you can call either `insert()` or `create()` on it, they are synonyms:

```python
await tonybar.insert()
await marsbar.create() # does exactly the same as insert()
```
You can also call `save()`, which behaves the same for new documents, but will also update existing documents. See the [section on updating](updating-&-deleting.md) of this tutorial for more details.

If you prefer you can also call the `insert_one` classmethod: 
```python
await Product.insert_one(tonybar)
```

## Inserting many documents

To reduce the number of database queries, similarly typed documents should be inserted together by calling the classmethod `insert_many`.
```python
await Product.insert_many([tonybar,marsbar])
```
