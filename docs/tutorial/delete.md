# Delete Documents

## Single Document

Delete one document fetched by a query or by id:

```python
# Via a query
await Product.find_one(Product.name == "Milka").delete()

# Via a fetched instance
bar = await Product.find_one(Product.name == "Milka")
if bar is not None:
    await bar.delete()

# Via id
product = await Product.get(product_id)
if product is not None:
    await product.delete()
```

## Many Documents

Delete all documents matching a filter:

```python
await Product.find(Product.category.name == "Chocolate").delete()
```

## All Documents

Delete every document in the collection:

```python
await Product.delete_all()
# Equivalent to:
await Product.find().delete()
```

## Delete with Relations (DeleteRules)

When a document has `Link` fields pointing to other documents, you can control
what happens to those linked documents on deletion using `DeleteRules`.

```python
from beanie import Document, Link, DeleteRules


class Author(Document):
    name: str


class Article(Document):
    title: str
    author: Link[Author]
```

**`DO_NOTHING` (default)** — the linked `Author` is left untouched.  Only
the `Article` is removed:

```python
await article.delete(link_rule=DeleteRules.DO_NOTHING)
```

**`DELETE_LINKS`** — each linked document is also deleted recursively:

```python
await article.delete(link_rule=DeleteRules.DELETE_LINKS)
# The referenced Author is deleted too
```

> **Caution:** `DELETE_LINKS` performs individual delete calls for each link.
> For bulk operations consider handling relation cleanup manually.

## Bulk Deletion

Use `BulkWriter` when deleting many documents in a batch to reduce database
round-trips:

```python
async with Product.bulk_writer() as bulk:
    for product_id in ids_to_delete:
        product = await Product.get(product_id)
        if product:
            await product.delete(bulk_writer=bulk)
# All deletes are sent to MongoDB in a single bulk write
```

## Soft Delete

If you want to keep documents in the database but mark them as deleted, inherit
from `DocumentWithSoftDelete` instead of `Document`.  See the
[Soft Delete tutorial](soft_delete.md) for full details.

```python
from beanie import DocumentWithSoftDelete


class Article(DocumentWithSoftDelete):
    title: str


article = await Article.find_one(Article.title == "Hello")
await article.delete()          # sets deleted_at timestamp, does NOT remove from DB
await article.hard_delete()     # permanently removes from DB
```

## Session Support

All delete operations accept an optional `session` parameter for use inside
MongoDB transactions:

```python
async with await client.start_session() as session:
    async with session.start_transaction():
        await article.delete(session=session)
        await author.delete(session=session)
```

## Return Value

Instance `delete()` returns a `DeleteResult` from pymongo.  Class-level
`find(...).delete()` also returns a `DeleteResult`:

```python
result = await Product.find(Product.price < 0).delete()
print(result.deleted_count)
```
