# Soft Delete

Instead of permanently removing documents from the database, soft delete marks them as deleted by setting a `deleted_at` timestamp. Soft-deleted documents are automatically excluded from normal queries but remain in the database.

## Defining a document

To enable soft delete, inherit from `DocumentWithSoftDelete` instead of `Document`:

```python
from beanie import DocumentWithSoftDelete


class Product(DocumentWithSoftDelete):
    name: str
    price: float
```

This adds an optional `deleted_at` field to your document automatically.

## Deleting

Calling `delete()` on a soft-delete document does not remove it from the database. It sets `deleted_at` to the current UTC timestamp:

```python
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()

bar.is_deleted()  # True
bar.deleted_at    # datetime(...)
```

## Finding documents

Standard query methods automatically exclude soft-deleted documents:

```python
# These only return non-deleted documents
product = await Product.find_one(Product.name == "Milka")
products = await Product.find_many().to_list()
products = await Product.find().to_list()
```

To include soft-deleted documents, use `find_many_in_all()`:

```python
# Returns all documents, including soft-deleted ones
all_products = await Product.find_many_in_all().to_list()
```

## Hard delete

To permanently remove a soft-delete document from the database:

```python
bar = await Product.find_one(Product.name == "Milka")
await bar.hard_delete()
```

After a hard delete, the document is gone from the database entirely and will not appear in `find_many_in_all()` results either.
