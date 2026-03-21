# Beanie Cheatsheet

Quick reference for the most common Beanie patterns.

---

## Setup

```python
import motor.motor_asyncio
from beanie import init_beanie, Document

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

await init_beanie(
    database=client.my_database,
    document_models=[Product, Author, Article],  # all Document subclasses
)
```

---

## Define a Document

```python
from beanie import Document, Indexed
from pydantic import Field
from bson import ObjectId


class Product(Document):
    name: Indexed(str, unique=True)   # creates a unique index
    price: float
    category: str = "general"
    tags: list[str] = []

    class Settings:
        name = "products"             # MongoDB collection name
        use_state_management = True   # enables is_changed, get_changes, rollback
        validate_on_save = True       # validates before every write
```

---

## Insert

```python
# Single insert
product = Product(name="Widget", price=9.99)
await product.insert()

# Shorthand (alias for insert)
await product.create()

# Insert many
await Product.insert_many([
    Product(name="A", price=1.0),
    Product(name="B", price=2.0),
])
```

---

## Find

```python
# By id
product = await Product.get(product_id)            # returns None if not found

# Find one
product = await Product.find_one(Product.name == "Widget")

# Find many → list
products = await Product.find(Product.price < 50).to_list()

# Chaining
products = await (
    Product.find(Product.category == "tech")
    .sort(-Product.price)    # descending
    .skip(10)
    .limit(5)
    .to_list()
)

# All documents
all_products = await Product.find_all().to_list()
# or
all_products = await Product.find().to_list()

# Count
n = await Product.find(Product.price > 10).count()

# Exists check
exists = await Product.find(Product.name == "Widget").exists()

# Distinct values
categories = await Product.distinct("category")
```

---

## Update

```python
# Update via instance
product.price = 12.99
await product.save()              # full replace
await product.save_changes()      # only changed fields ($set)

# Update operators (no fetch required)
await product.set({Product.price: 12.99})
await product.inc({Product.price: 1.0})
await product.current_date({Product.updated_at: True})

# Update many
await Product.find(Product.category == "old").update(
    {"$set": {"category": "archive"}}
)

# Upsert
await Product.find_one(Product.name == "Widget").upsert(
    {"$set": {"price": 9.99}},
    on_insert=Product(name="Widget", price=9.99),
)
```

---

## Delete

```python
# Single
await product.delete()

# Via query
await Product.find_one(Product.name == "Widget").delete()

# Many
await Product.find(Product.price < 0).delete()

# All
await Product.delete_all()
```

---

## Projections

```python
from pydantic import BaseModel


class ProductSummary(BaseModel):
    name: str
    price: float


summaries = await Product.find().project(ProductSummary).to_list()
```

---

## Relations

```python
from beanie import Link, BackLink, WriteRules, DeleteRules
from pydantic import Field


class Author(Document):
    name: str
    articles: list[BackLink["Article"]] = Field(
        original_field="author", default=[]
    )


class Article(Document):
    title: str
    author: Link[Author]
    tags: list[Link[Tag]] = []
```

```python
# Insert with linked document creation
article = Article(title="Hello", author=author_instance)
await article.insert(link_rule=WriteRules.WRITE)  # also inserts author

# Fetch one link field
await article.fetch_link(Article.author)
print(article.author.name)

# Fetch all link fields at once
await article.fetch_all_links()

# Query with auto-fetch
article = await Article.find_one(
    Article.title == "Hello",
    fetch_links=True,
)

# Delete and cascade
await article.delete(link_rule=DeleteRules.DELETE_LINKS)

# Build a link without fetching
article.author = Author.link_from_id(known_author_id)
await article.save()
```

---

## Event Hooks (Actions)

```python
from beanie import before_event, after_event, Insert, Save, Delete


class Article(Document):
    title: str
    slug: str

    @before_event(Insert)
    def generate_slug(self):
        self.slug = self.title.lower().replace(" ", "-")

    @before_event([Save, Insert])
    async def validate_title(self):
        if len(self.title) < 3:
            raise ValueError("Title too short")

    @after_event(Delete)
    async def cleanup(self):
        await notify_deleted(self.id)
```

---

## Bulk Writes

```python
async with Product.bulk_writer() as bulk:
    await Product(name="A", price=1.0).insert(bulk_writer=bulk)
    await Product(name="B", price=2.0).insert(bulk_writer=bulk)
    await Product.find_one(Product.name == "Old").delete(bulk_writer=bulk)
# All operations sent in a single round-trip on context exit
```

---

## State Management

```python
class Product(Document):
    price: float

    class Settings:
        use_state_management = True
        save_previous_state = True   # required for has_changed / get_previous_changes


product = await Product.find_one(...)
product.price = 99.0

if product.is_changed:
    print(product.get_changes())         # {"price": 99.0}

await product.save()
print(product.get_previous_changes())    # {"price": <old value>}

# Discard unsaved changes
product.rollback()
```

---

## Aggregations

```python
# Built-in
avg = await Product.avg(Product.price)
total = await Product.sum(Product.price)
minimum = await Product.min(Product.price)
maximum = await Product.max(Product.price)

# Scoped
avg_tech = await Product.find(Product.category == "tech").avg(Product.price)

# Custom pipeline
from pydantic import BaseModel, Field


class CategoryStats(BaseModel):
    id: str = Field(alias="_id")
    avg_price: float
    count: int


stats = await Product.aggregate(
    [
        {"$group": {"_id": "$category", "avg_price": {"$avg": "$price"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_price": -1}},
    ],
    projection_model=CategoryStats,
).to_list()
```

---

## Indexes

```python
from beanie import Document, Indexed
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from pydantic import Field
from typing import Annotated


class Article(Document):
    # Single-field index via Indexed()
    title: Indexed(str)
    # Unique index
    slug: Indexed(str, unique=True)
    # Annotated syntax
    author_id: Annotated[str, Indexed()]

    class Settings:
        name = "articles"
        indexes = [
            # Compound index
            IndexModel([("title", ASCENDING), ("author_id", ASCENDING)]),
            # Full-text index
            IndexModel([("title", TEXT)]),
        ]
```

---

## Inheritance

```python
from beanie import Document


class Shape(Document):
    color: str

    class Settings:
        name = "shapes"
        is_root = True            # store all subtypes in one collection


class Circle(Shape):
    radius: float


class Rectangle(Shape):
    width: float
    height: float


# Insert subtypes
await Circle(color="red", radius=5.0).insert()
await Rectangle(color="blue", width=3.0, height=4.0).insert()

# Query all shapes (polymorphic)
all_shapes = await Shape.find_all().to_list()

# Query only circles
circles = await Circle.find_all().to_list()
```

---

## Soft Delete

```python
from beanie import DocumentWithSoftDelete


class Post(DocumentWithSoftDelete):
    title: str


post = await Post.find_one(Post.title == "Draft")
await post.delete()             # marks deleted_at, stays in DB

# Only non-deleted posts
active = await Post.find_all().to_list()

# Include soft-deleted
all_posts = await Post.find_many_in_all().to_list()

# Permanent removal
await post.hard_delete()
```

---

## Revision (Optimistic Concurrency)

```python
from beanie.exceptions import RevisionIdWasChanged


class Account(Document):
    balance: float

    class Settings:
        use_revision = True


account = await Account.get(account_id)
account.balance += 100.0

try:
    await account.save()
except RevisionIdWasChanged:
    # Another process modified the document — re-fetch and retry
    account = await Account.get(account_id)
    ...
```

---

## Sessions & Transactions

```python
async with await client.start_session() as session:
    async with session.start_transaction():
        await product.insert(session=session)
        await stock.update({"$inc": {"qty": -1}}, session=session)
```

---

## Migrations

```bash
# Create a new migration file
beanie new-migration -n add_slug_field -p ./migrations

# Run all pending migrations
beanie migrate -uri mongodb://localhost/mydb -db mydb -p ./migrations
```

```python
# migrations/20240101_add_slug_field.py
from beanie.migrations.models import RunningDirections

async def migrate(db, session=None):
    await db["articles"].update_many(
        {"slug": {"$exists": False}},
        [{"$set": {"slug": {"$toLower": "$title"}}}],
        session=session,
    )

async def backward(db, session=None):
    await db["articles"].update_many(
        {}, {"$unset": {"slug": ""}}, session=session
    )
```
