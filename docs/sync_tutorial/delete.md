# Delete documents

Beanie supports single and batch deletions:

## Single

```python

Product.find_one(Product.name == "Milka").delete().run()

# Or
bar = Product.find_one(Product.name == "Milka").run()
bar.delete()
```

## Many

```python

Product.find(Product.category.name == "Chocolate").delete().run()
```

## All

```python

Product.delete_all()
# Or
Product.all().delete().run()

```