# State Management

Beanie can keep the document state, that synced with the database, to find local changes and save only them.

This feature must be turned on in the `Settings` inner class explicitly:

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

## Options

By default, state management will merge the changes made to nested objects, which is fine for most cases,
as it is non-destructive, and does not re-assign the whole object is only one of its attributes changed:

```python
from typing import Dict


class Item(Document):
    name: str
    attributes: Dict[str, float]

    class Settings:
        use_state_management = True
```

```python
i = Item(name="Test", attributes={"attribute_1": 1.0, "attribute_2": 2.0})
await i.insert()
i.attributes = {"attribute_1": 1.0}
await i.save_changes()
# Changes will consist of: {"attributes.attribute_1": 1.0}
# Keeping attribute_2
```

However, there's some cases where you want to replace the whole object when one of its attributes changed.
You can enable the `state_management_replace_objects` attribute in your model's `Settings` inner class:

```python
from typing import Dict


class Item(Document):
    name: str
    attributes: Dict[str, float]

    class Settings:
        use_state_management = True
        state_management_replace_objects = True
```

With this setting activated, when one attribute of the nested object is changed, the whole object will be overridden:

```python
i = Item(name="Test", attributes={"attribute_1": 1.0, "attribute_2": 2.0})
await i.insert()
i.attributes.attribute_1 = 1.0
await i.save_changes()
# Changes will consist of: {"attributes.attribute_1": 1.0, "attributes.attribute_2": 2.0}
# Keeping attribute_2
```

When the whole object is assigned, the whole nested object will be overridden:

```python
i = Item(name="Test", attributes={"attribute_1": 1.0, "attribute_2": 2.0})
await i.insert()
i.attributes = {"attribute_1": 1.0}
await i.save_changes()
# Changes will consist of: {"attributes": {"attribute_1": 1.0}}
# Removing attribute_2
```
