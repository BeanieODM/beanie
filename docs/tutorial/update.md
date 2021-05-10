# Update documents

[UpdateOne](/beanie/api/queries/#updateone) and [UpdateMany](/beanie/api/queries/#updatemany) queries are used to update single and many documents respectively.

[Document](/beanie/api/document/), [FindOne](/beanie/api/queries/#findone), [FindMany](/beanie/api/queries/#findmany), and both update query instances implement [UpdateMethods](/beanie/api/interfaces/#updatemethods) interface including `update` method.  

## By method from UpdateMethods interface

### Entity
```python
await product.set({Product.price: 3.33})
```

### Single
```python
await Product.find_one(Product.name == "Milka").set({Product.price: 3.33})
```

### Many
```python
await Product.find(Product.category.name == "Chocolate").inc({Product.price: 1})
```

## By operator class

Most of the update query operators are wrapped as operator classes. The whole list could be found [by link](/beanie/api/operators/update/)

### Entity
```python
await product.update(Set({Product.price: 3.33}))
```

### Single
```python
await Product.find_one(Product.name == "Milka").update(Set({Product.price: 3.33}))
```

### Many
```python
await Product.find(Product.category.name == "Chocolate").update(Inc({Product.price: 1}))
```

## By native syntax

### Entity
```python
await product.update({"$set": {Product.price: 3.33}})
```

### Single
```python
await Product.find_one(Product.name == "Milka").update({"$set": {Product.price: 3.33}})
```

### Many
```python
await Product.find(Product.category.name == "Chocolate"
                   ).update({"$inc": {Product.price: 1}})
```