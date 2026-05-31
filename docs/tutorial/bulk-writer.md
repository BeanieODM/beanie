# Bulk operations with `BulkWriter`

When you need to issue many writes to MongoDB at once, batching them into a
single bulk request is dramatically faster than sending each one
individually. Beanie exposes this through `BulkWriter`, an async context
manager that collects operations and commits them in one round-trip when
the block exits.

## Quick example

```python
import asyncio

from beanie import BulkWriter, Document, init_beanie
from pymongo import AsyncMongoClient


class Product(Document):
    name: str
    price: float


async def main() -> None:
    client = AsyncMongoClient("mongodb://localhost:27017")
    await init_beanie(database=client.shop, document_models=[Product])

    async with BulkWriter() as bw:
        await Product(name="apple", price=1.0).insert(bulk_writer=bw)
        await Product(name="banana", price=0.5).insert(bulk_writer=bw)
        await Product(name="cherry", price=2.5).insert(bulk_writer=bw)
    # All three inserts are sent in one bulk write when the `async with`
    # block exits.

asyncio.run(main())
```

Without `BulkWriter` the three `.insert(...)` calls would issue three
separate writes; with it, the operations queue locally and ship as a
single `bulk_write` to the collection.

## Mixing operation types

A single `BulkWriter` can hold inserts, replaces, updates, and deletes —
they're committed together as long as they target the same collection.

```python
async with BulkWriter() as bw:
    # Insert a new document
    await Product(name="durian", price=8.0).insert(bulk_writer=bw)

    # Replace an existing one
    existing = await Product.find_one(Product.name == "apple")
    if existing is not None:
        existing.price = 1.2
        await existing.replace(bulk_writer=bw)

    # Update via a query
    await Product.find(Product.price < 1.0).update(
        {"$set": {"price": 1.0}},
        bulk_writer=bw,
    )

    # Delete via a query
    await Product.find(Product.name == "cherry").delete(bulk_writer=bw)
# All four operations are issued in a single bulk_write at this point.
```

The methods that take a `bulk_writer` keyword include `insert`,
`insert_many`, `replace`, `save`, `save_changes`, `update`, `set`, `inc`,
and `delete` (and the matching variants on the find/update/delete query
chains).

## Manual commit

If you don't want context-manager semantics, you can construct a
`BulkWriter` directly and commit it yourself:

```python
bw = BulkWriter()
await Product(name="elderberry", price=3.0).insert(bulk_writer=bw)
await Product(name="fig", price=2.0).insert(bulk_writer=bw)

result = await bw.commit()
# result is a pymongo BulkWriteResult, or None if no operations were queued.
```

The `async with` form is preferred when you can use it — it guarantees
`commit()` runs even if an exception is raised inside the block (well,
to be precise: it runs only on a clean exit, the same way a regular
context manager works; on exception the queued operations are dropped
intentionally).

## Constructor options

```python
BulkWriter(
    session=None,                     # pymongo AsyncClientSession for transactions
    ordered=True,                     # stop at the first failure (True) or attempt all (False)
    object_class=None,                # set explicitly when not using helper methods
    bypass_document_validation=False, # skip MongoDB schema validation
    comment=None,                     # attached to the bulk command, surfaces in MongoDB logs/profiler
)
```

In most flows you don't need to set `object_class` — Beanie infers it
from the first operation added through `Document.insert(bulk_writer=...)`
or similar. You only need to pass it when you build operations through
lower-level APIs.

## Same collection only

All operations queued on a single `BulkWriter` must target the same
collection. If you mix collections you'll get:

```
ValueError: All the operations should be for a same collection name
```

Use one `BulkWriter` per collection.
