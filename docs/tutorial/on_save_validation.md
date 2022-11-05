# On save validation

Pydantic has a very useful config to validate values on assignment - `validate_assignment = True`. 
But, unfortunately, this is an expensive operation and doesn't fit some use cases.
You can validate all the values before saving the document (`insert`, `replace`, `save`, `save_changes`) 
with beanie config `validate_on_save` instead.

This feature must be turned on in the `Settings` inner class explicitly:

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        validate_on_save = True
```

If any field has a wrong value, 
it will raise an error on write operations (`insert`, `replace`, `save`, `save_changes`).

```python
sample = Sample.find_one(Sample.name == "Test")
sample.num = "wrong value type"

# Next call will raise an error
await sample.replace()
```
