# Insert the documents

## Insert single

```python
chocolate = Category(name="Chocolate")

bar = Product(name="Tony's", price=5.95, category=chocolate)
await bar.insert()
```
OR
```python
bar = Product(name="Tony's", price=5.95, category=chocolate)
await bar.create()
```
OR
```python
bar = Product(name="Tony's", price=5.95, category=chocolate)
await Product.insert_one(bar)
```

## Insert many

```python
milka = Product(name="Milka", price=3.05, category=chocolate)
peanut_bar = Product(name="Peanut Bar", price=4.44, category=chocolate)
await Product.insert_many([milka, peanut_bar])
```
