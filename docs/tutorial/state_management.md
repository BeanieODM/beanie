# State Management

Beanie can keep the document state synced with the database in order to find local changes and save only them.

This feature must be explicitly turned on in the `Settings` inner class:

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_state_management = True
```

Beanie keeps the current changes (not yet saved in the database) by default (with `use_state_management = True`), AND the previous changes (saved to the database) with `state_management_save_previous = True`.

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_state_management = True
        state_management_save_previous = True
```

Every new save override the previous changes and clears the current changes.

## Saving changes

To save only changed values, the `save_changes()` method should be used.

```python
s = await Sample.find_one(Sample.name == "Test")
s.num = 100
await s.save_changes()
```

The `save_changes()` method can only be used with already inserted documents.


## Interacting with changes

Beanie exposes several methods that can be used to interact with the saved changes:

```python
s = await Sample.find_one(Sample.name == "Test")

s.is_changed == False
s.get_changes == {}

s.num = 200

s.is_changed == True
s.get_changes() == {"num": 200}

s.rollback()

s.is_changed == False
s.get_changes() == {}
```

And similar methods can be used with the previous changes that have been saved in the database if `state_management_save_previous` is set to `True`:

```python
s = await Sample.find_one(Sample.name == "Test")

s.num = 200
await s.save_changes()

s.has_changed == True
s.get_previous_changes() == {"num": 200}
s.get_changes() == {}
```


## Options

By default, state management will merge the changes made to nested objects, 
which is fine for most cases as it is non-destructive and does not re-assign the whole object 
if only one of its attributes changed:

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

However, there are some cases where you would want to replace the whole object when one of its attributes changed.
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

With this setting activated, the whole object will be overridden when one attribute of the nested object is changed:

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
