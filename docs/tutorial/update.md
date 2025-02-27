# Updating & Deleting

Now that we know how to find documents, how do we change them or delete them?

## Saving changes to existing documents

The easiest way to change a document in the database is to use either the `replace` or `save` method on an altered document. 
These methods both write the document to the database, 
but `replace` will raise an exception when the document does not exist yet, while `save` will insert the document. 

Using `save()` method:

```python
bar = await Product.find_one(Product.name == "Mars")
bar.price = 10
await bar.save()
```

Otherwise, use the `replace()` method, which throws:
- a `ValueError` if the document does not have an `id` yet, or
- a `beanie.exceptions.DocumentNotFound` if it does, but the `id` is not present in the collection

```python
bar.price = 10
try:
    await bar.replace()
except (ValueError, beanie.exceptions.DocumentNotFound):
    print("Can't replace a non existing document")
```

> ⚠️ **Important**: Both `save()` and `replace()` methods update the **entire document** in the database, even if you only changed one field. This can lead to:
> 
> - **Performance issues**: Sending and processing the entire document is less efficient than updating just changed fields
> - **Data loss**: If another process modified different fields of the same document since you retrieved it, those changes will be overwritten

To avoid these issues, two alternatives are available:

1. **State Management**: Use [State Management](state_management.md) with `save_changes()` method to track and update only modified fields
2. **Update Queries**: Use database-level update operations as described below for direct field updates

## Update queries

Update queries can be performed on the result of a `find` or `find_one` query, 
or on a document that was returned from an earlier query. 
Simpler updates can be performed using the `set`, `inc`, and `current_date` methods:

```python
bar = await Product.find_one(Product.name == "Mars")
await bar.set({Product.name:"Gold bar"})
bar = await Product.find(Product.price > .5).inc({Product.price: 1})
```

More complex update operations can be performed by calling `update()` with an update operator, similar to find queries:

```python
await Product.find_one(Product.name == "Tony's").update(Set({Product.price: 3.33}))
```

The whole list of the update query operators can be found [here](../api-documentation/operators/update.md).

Native MongoDB syntax is also supported:

```python
await Product.find_one(Product.name == "Tony's").update({"$set": {Product.price: 3.33}})
```

## Upsert

To insert a document when no documents are matched against the search criteria, the `upsert` method can be used:

```python
await Product.find_one(Product.name == "Tony's").upsert(
    Set({Product.price: 3.33}), 
    on_insert=Product(name="Tony's", price=3.33, category=chocolate)
)
```

## Deleting documents

Deleting objects works just like updating them, you simply call `delete()` on the found documents:

```python
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()

await Product.find_one(Product.name == "Milka").delete()

await Product.find(Product.category.name == "Chocolate").delete()
```

## Response Type

For the object methods `update` and `upsert`, you can use the `response_type` parameter to specify the type of response.

The options are:
- `UpdateResponse.UPDATE_RESULT` - returns the result of the update operation.
- `UpdateResponse.NEW_DOCUMENT` - returns the newly updated document.
- `UpdateResponse.OLD_DOCUMENT` - returns the document before the update.
