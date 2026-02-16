# Event-based actions

You can register methods as pre- or post- actions for document events.

Currently supported events:

- Save
- Insert
- Replace
- Update
- SaveChanges
- Delete
- ValidateOnSave

Currently supported directions:

- `Before`
- `After`

Current operations creating events:

- `insert()` for Insert
- `replace()` for Replace
- `save()` for Save and triggers Insert if it is creating a new document, or triggers Replace if it replaces an existing document
- `save_changes()` for SaveChanges
- `insert()`, `replace()`, `save_changes()`, and `save()` for ValidateOnSave
- `set()`, `update()` for Update
- `delete()` for Delete

To register an action, you can use `@before_event` and `@after_event` decorators respectively:

```python
from beanie import Insert, Replace, before_event, after_event


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
from beanie import Insert, Replace, before_event


class Sample(Document):
    num: int
    name: str

    @before_event(Insert, Replace)
    def capitalize_name(self):
        self.name = self.name.capitalize()
```

This will capitalize the `name` field value before each document's Insert and Replace.

And sync and async methods could work as actions.

```python
from beanie import Insert, Replace, after_event


class Sample(Document):
    num: int
    name: str

    @after_event(Insert, Replace)
    async def send_callback(self):
        await client.send(self.id)
```

Actions can be selectively skipped by passing the `skip_actions` argument when calling
the operations that trigger events. `skip_actions` accepts a list of directions and action names.

```python
from beanie import After, Before, Insert, Replace, before_event, after_event


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

## Update event and field modifications

When using `@before_event(Update)`, you can modify document fields and those changes will 
be included in the update operation sent to MongoDB. This allows patterns like automatically
setting an `updated_at` timestamp:

```python
from datetime import datetime, timezone

from beanie import Document, Update, before_event


class Sample(Document):
    name: str
    updated_at: datetime | None = None

    @before_event(Update)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)
```

When `sample.set({"name": "new_name"})` is called, the `updated_at` field will also be
included as a `$set` operation in the update expression.

### Conflict resolution

A conflict occurs when both the explicit update arguments and a `@before_event` handler
modify the same field. You can control how these conflicts are resolved using the
`action_conflict_resolution` setting:

```python
from beanie import Document, ActionConflictResolution


class Sample(Document):
    name: str
    
    class Settings:
        action_conflict_resolution = ActionConflictResolution.ACTION_WINS
```

Available strategies:

| Strategy | Description |
|---|---|
| `UPDATE_WINS` (default) | Explicit update arguments take precedence. Action changes are included only for fields not already targeted by the update. |
| `ACTION_WINS` | Action changes take precedence. For conflicting fields, the before_event value replaces what the update expression would have set. |
| `ACTION_OVERRIDE` | Action changes completely replace the entire update expression. The original update arguments are discarded. |
| `RAISE` | Raises `MergeConflictError` if any field is modified by both the update and a before_event handler. |

Example with `RAISE`:

```python
from beanie import (
    Document,
    Update,
    ActionConflictResolution,
    MergeConflictError,
    before_event,
)


class StrictSample(Document):
    name: str
    counter: int = 0

    @before_event(Update)
    def increment_counter(self):
        self.counter += 1

    class Settings:
        action_conflict_resolution = ActionConflictResolution.RAISE


sample = StrictSample(name="test")
await sample.insert()

# This works fine — no conflict (update touches "name", action touches "counter")
await sample.set({StrictSample.name: "updated"})

# This raises MergeConflictError — both update and action modify "counter"
try:
    await sample.set({StrictSample.counter: 100})
except MergeConflictError as e:
    print(e.conflicting_fields)  # {"counter"}
```
