## Migrate from async

Since version `1.13.0` Beanie supports synchronous interfaces as well as async. Nearly all the syntax is the same. But there are a few significant changes.
## Import

Most of the entities should be imported from `beanie.sync` instead of just `beanie`. For example, the Document class:

```python
from beanie.sync import Document

class Product(Document):
    name: str
    price: float
```

## Init

As it is a synchronous version, a sync client should be used for the initialization.

```python
from pymongo import MongoClient

from beanie.sync import init_beanie


cli = MongoClient("mongodb://localhost:27017")
db = cli.products_db

init_beanie(database=db, document_models=[Product])
```

## Queries

For query objects `FindOne`, `UpdateQuery`, and `DeleteQuery` you need to call the additional `run()` method at the end of the methods chain to fetch/commit. As a syntax sugar it can be replaced with `~` prefix.

### Find

Get
```python
bar = Product.get("608da169eb9e17281f0ab2ff").run()
# or
bar = ~Product.get("608da169eb9e17281f0ab2ff")
```

Find one
```python
bar = Product.find_one(Product.name == "Peanut Bar").run()
# or
bar = ~Product.find_one(Product.name == "Peanut Bar")
```

For find many you don't need to call `run()` method, as it is iterator:

```python
for result in Product.find(search_criteria):
    print(result)

# or

result = Product.find(search_criteria).to_list()
```

### Update

Update one
```python
Product.find_one(Product.name == "Tony's").update({"$set": {Product.price: 3.33}}).run()
# or
~Product.find_one(Product.name == "Tony's").update({"$set": {Product.price: 3.33}})
```

BTW update of the already fetched object works without calling the `run` method as it doesn't return `UpdateQuery` in result
```python
bar = Product.find_one(Product.name == "Milka").run()
bar.update({"$set": {Product.price: 3.33}})
```

Update many
```python
Product.find(Product.price <= 2).update({"$set": {Product.price: 3.33}}).run()
# or
~Product.find(Product.price <= 2).update({"$set": {Product.price: 3.33}})
```

### Delete

Single
```python
Product.find_one(Product.name == "Milka").delete().run()

# or

~Product.find_one(Product.name == "Milka").delete()

# or

bar = Product.find_one(Product.name == "Milka").run()
bar.delete()
```

Many
```python
Product.find(Product.category.name == "Chocolate").delete().run()

# or

~Product.find(Product.category.name == "Chocolate").delete()
```