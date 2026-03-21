# Lazy Parsing

## What is Lazy Parsing?

By default, when Beanie fetches documents from MongoDB, Pydantic validates and
parses every field immediately — coercing types, running validators, and
building nested models.  This is the safest option and is recommended for most
use cases.

**Lazy parsing** defers that work: the raw BSON data is stored as-is and
each field is only validated when it is first accessed.  This can speed up
queries that retrieve large documents but only read a small subset of their
fields.

## When to Use Lazy Parsing

Consider lazy parsing when:

- You are retrieving many documents but only reading one or two fields from
  each.
- The documents contain large embedded sub-documents or arrays that you do not
  need for a particular operation.
- Profiling has shown that Pydantic validation is a measurable bottleneck for
  your specific query.

Do **not** use lazy parsing when:

- You need all fields to be validated upfront (e.g. for data integrity checks).
- You are passing documents across async boundaries where the access order is
  unpredictable.
- Your document models use validators that have side effects.

## Basic Usage

Pass `lazy_parse=True` to any `find` / `find_many` query:

```python
from beanie import Document, init_beanie
from pydantic import Field
import motor.motor_asyncio


class Product(Document):
    name: str
    price: float
    description: str  # large field we don't need here
    tags: list[str] = []

    class Settings:
        name = "products"


# Only `name` will be validated on access; other fields stay raw until touched
products = await Product.find(
    Product.price < 50.0,
    lazy_parse=True,
).to_list()

for p in products:
    print(p.name)   # validated here
    # p.description is not validated until this line is reached
```

## Lazy Parsing with Projections

Combining lazy parsing with a projection is the most effective pattern —
MongoDB only returns the fields you need, and Pydantic skips validation for
anything not present:

```python
from pydantic import BaseModel


class ProductSummary(BaseModel):
    name: str
    price: float


summaries = await Product.find(
    Product.price < 50.0,
    lazy_parse=True,
).project(ProductSummary).to_list()
```

## Field Access and Validation

When you access a field on a lazily parsed document, the value is validated
at that moment.  If the raw value does not pass validation, a `ValidationError`
is raised at access time rather than at query time:

```python
# Suppose a document in the DB has `price: "not-a-number"` (corrupt data)
products = await Product.find(lazy_parse=True).to_list()

for p in products:
    try:
        print(p.price)       # ValidationError raised HERE, not during find()
    except Exception as e:
        print(f"Validation failed for {p.id}: {e}")
```

This means lazy parsing shifts error discovery from query time to field access
time.  Keep this in mind when writing error-handling code.

## Caveats and Limitations

| Concern | Detail |
|---|---|
| **Error timing** | Validation errors surface on field access, not on query execution |
| **Not thread/task safe by default** | If multiple coroutines access the same lazy document concurrently, validate once first |
| **No guarantee of full validation** | Code paths that never touch a field will never validate it |
| **Compatibility with `fetch_links`** | Link fields are still fetched eagerly; `lazy_parse` only affects non-link field validation |
