# Delete documents

Beanie supports single and batch deletions:

## Single

```python

await Product.find_one(Product.name == "Milka").delete()

# Or
bar = await Product.find_one(Product.name == "Milka")
await bar.delete()
```

## Many

```python

await Product.find(Product.category.name == "Chocolate").delete()
```

## All

```python

await Product.delete_all()
# Or
await Product.all().delete()

```