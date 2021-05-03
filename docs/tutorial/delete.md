Text about find and delete

```python
# Single 
await Product.find_one(Product.name == "Milka").delete()

# Or
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()

# Many
await Product.find(Product.category.name == "Chocolate").delete()

# All
await Product.delete_all()
# Or
await Product.all().delete()

```