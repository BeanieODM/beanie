# Save changes

Beanie can keep the document state, that synced with the database, to find local changes and save only them.

This feature must be turned on in the `Settings` inner class explicitly.

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_state_management = True
```

To save only changed values the `save_changes()` method should be used.

```python
s = await Sample.find_one(Sample.name == "Test")
s.num = 100
await s.save_changes()
```

The `save_changes()` method can be used only with already inserted documents.