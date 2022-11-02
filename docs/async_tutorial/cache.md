# Cache
All query results could be locally cached.

This feature must be explicitly turned on in the `Settings` inner class.

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_cache = True
```

Beanie uses LRU cache with expiration time. 
You can set `capacity` (the maximum number of the cached queries) and expiration time in the `Settings` inner class.

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_cache = True
        cache_expiration_time = datetime.timedelta(seconds=10)
        cache_capacity = 5
```

Any query will be cached for this document class.

```python
# on the first call it will go to the database
samples = await Sample.find(num>10).to_list()

# on the second - it will use cache instead
samples = await Sample.find(num>10).to_list()

await asyncio.sleep(15)

# if the expiration time was reached it will go to the database again
samples = await Sample.find(num>10).to_list()
```