# Event-based actions

You can register methods as pre- or post- actions for document events.

Currently supported events:
- Insert
- Replace
- SaveChanges
- ValidateOnSave
- Update

Currently supported directions:

- `Before`
- `After`

Current operations creating events:
- `insert()` for Insert
- `replace()` Replace
- `save()` triggers Insert if it is creating a new document, triggers Replace it replaces existing document.
- `save_changes()` for SaveChanges
- `insert()`, `replace()`, `save_changes()`, and `save()` for ValidateOnSave
- `set()`, `update()` for Update

To register an action, you can use `@before_event` and `@after_event` decorators respectively:

```python
from beanie import Insert, Replace


class Sample(Document):
    num: int
    name: str

    @before_event(Insert)
    def capitalize_name(self):
        self.name = self.name.capitalize()

    @after_event(Replace)
    def num_change(self):
        self.num -= 1
```

It is possible to register action for several events:

```python
from beanie import Insert, Replace


class Sample(Document):
    num: int
    name: str

    @before_event(Insert, Replace)
    def capitalize_name(self):
        self.name = self.name.capitalize()
```

This will capitalize the `name` field value before each document insert and replace.

And sync and async methods could work as actions.

```python
from beanie import Insert, Replace


class Sample(Document):
    num: int
    name: str

    @after_event(Insert, Replace)
    async def send_callback(self):
        await client.send(self.id)
```

Actions can be selectively skipped by passing the parameter `skip_actions` when calling
the operations that trigger events. `skip_actions` accepts a list of directions and action names.

```python
from beanie import After, Before, Insert, Replace


class Sample(Document):
    num: int
    name: str

    @before_event(Insert)
    def capitalize_name(self):
        self.name = self.name.capitalize()

    @before_event(Replace)
    def redact_name(self):
        self.name = "[REDACTED]"

    @after_event(Replace)
    def num_change(self):
        self.num -= 1


sample = Sample()

# capitalize_name will not be executed
await sample.insert(skip_actions=['capitalize_name'])

# num_change will not be executed
await sample.replace(skip_actions=[After])

# redact_name and num_change will not be executed
await sample.replace(skip_actions[Before, 'num_change'])
```
