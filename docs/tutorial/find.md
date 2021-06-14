To populate the database, please run the examples from the [previous section of the tutorial](insert.md) as we will be using the same setup here.


## Finding documents

The basic syntax for finding multiple documents in the database is to call the classmethod `find()` or it's synonym `find_many()` with some search criteria (see next section): 
```python
findresult = Product.find(search_criteria)
```
This returns a `FindMany` object which can be used to access the results in multiple ways. To loop through the results, use a `async for` loop"
```python
async for result in Product.find(search_criteria):
    print(result)
```
If you prefer a list of the results then you can call `to_list()`:
```python
result = await Product.find(search_criteria).to_list()
```

### Search criteria

As search criteria, Beanie supports python-based syntax.
For comparisons Python comparison operators can be used on the class fields (and nested
fields):
```python
products = await Product.find(Product.price < 10).to_list()
```

This is supported for the operators: `==`, `>`, `>=`, `<`, `<=`, `!=`.
Other MongoDB query operators can be used with the included wrappers. For example the `$in` operator can be used as follows:

```python
products = await Product.find(
    In(Product.category.name, ["Chocolate", "Fruits"])).to_list()
```

The whole list of the find query operators can be found [here](/api-documentation/operators/find).

For more complex cases native PyMongo syntax is also supported:

```python
products = await Product.find({"price": 1000}).to_list()
```

## Finding single documents

Sometimes you will only need to find a single document. If you are searching by `id` then you can use the [get](/api-documentation/document#get) method:

```python
bar = await Product.get("608da169eb9e17281f0ab2ff")
```

To find a single document via a searching criteria you can use the [find_one](/api-documentation/document#find_one) method:

```python
bar = await Product.find_one(Product.name == "Peanut Bar")
```

## More complex queries

### Multiple search criteria

If you have multiple search criteria to search for you can list them as separate arguments to any of the `find` functions:

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 5
).to_list()
```


Alternatively, you can chain `find` methods:

```python
chocolates = await Product
              .find(Product.category.name == "Chocolate")
              .find(Product.price < 5).to_list()
```

### Sorting

Sorting can be done with the [sort](/api-documentation/query#sort) method.

You can pass it one or multiple fields to sort by. You may optionally specify a `+` or `-` (denoting ascending and descending respectively).

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort(-Product.price,+Product.name).to_list()
```

You can also specify fields as strings or as tuples:

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort("-price","+name").to_list()

chocolates = await Product.find(
    Product.category.name == "Chocolate").sort(
    [
        (Product.price, pymongo.DESCENDING),
        (Product.name, pymongo.ASCENDING),
    ]
).to_list()
```

### Skip and limit

To skip a certain number of documents, or limit the total number of elements returned, the `skip`and `limit` methods can be used:
```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").skip(2).to_list()

chocolates = await Product.find(
    Product.category.name == "Chocolate").limit(2).to_list()
```

### Projections

When only part of a document is required projections can save a lot of database bandwidth and processing.
For simple projections we can just define a pydantic model with the required fields and pass it to `project()`:


```python
class ProductShortView(BaseModel):
    name: str
    price: float

chocolates = await Product.find(
    Product.category.name == "Chocolate").project(ProductShortView).to_list()
```

For more complex projections an inner `Settings` class with a `projection` field can be added:

```python
class ProductView(BaseModel):
    name: str
    category: str

    class Settings:
        projection = {"name": 1, "category": "$category.name"}

chocolates = await Product.find(
    Product.category.name == "Chocolate").project(ProductView).to_list()
```

### Finding all documents

If you every want to find all documents you can use the `find_all()` classmethod. This is equivalent to `find({})`.
