Text about query types FindOne and FindMany

# Basic usage

## One

By id

```python
bar = await Product.get("608da169eb9e17281f0ab2ff")
```

By parameter

```python
bar = await Product.find_one(Product.name == "Peanut Bar")
```

## Many

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 5
).to_list()
```

Text about cursor

```python
async for product in Product.find(
        Product.category.name == "Chocolate"
):
    print(product)
```

Text about chaining

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").find(
    Product.price < 5).to_list()
```

Text about operators

```python
chocolates = await Product.find(
    In(Product.category.name, ["Chocolate", "Fruits"])).find(
    Product.price < 5).to_list()
```

Text about sorting

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").sort(-Product.price).to_list()
```

Text about skip and limit

```python
chocolates = await Product.find(
    Product.category.name == "Chocolate").skip(2).to_list()

chocolates = await Product.find(
    Product.category.name == "Chocolate").limit(2).to_list()
```

Text about projections

```python

class ShortProduct(BaseModel):
    name: str
    price: float


chocolates = await Product.find(
    Product.category.name == "Chocolate").project(ShortProduct).to_list()
```
