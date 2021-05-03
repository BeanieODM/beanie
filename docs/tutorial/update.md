Text about single document and man documents updates

Text about methods and operators

By method

Single
```python
await Product.find_one(Product.name == "Milka").set({Product.price: 3.33})
```

Many
```python
await Product.find(Product.category.name == "Chocolate").inc({Product.price: 1})
```

By operator class

Single
```python
await Product.find_one(Product.name == "Milka").update(Set({Product.price: 3.33}))
```

Many
```python
await Product.find(Product.category.name == "Chocolate").update(Inc({Product.price: 1}))
```

By native syntax

Single
```python
await Product.find_one(Product.name == "Milka").update({"$set": {Product.price: 3.33}})
```

Many
```python
await Product.find(Product.category.name == "Chocolate"
                   ).update({"$inc": {Product.price: 1}})
```