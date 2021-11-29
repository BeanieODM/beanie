# Event-based actions

You can register methods as pre- or post- actions for document events like `insert`, `replace` and etc.

Currently supported events:

- Insert
- Replace
- SaveChanges
- ValidateOnSave

To register an action you can use `@before_event` and `@after_event` decorators respectively.

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

It is possible to register action for a list of events:

```python
from beanie import Insert, Replace

class Sample(Document):
    num: int
    name: str

    @before_event([Insert, Replace])
    def capitalize_name(self):
        self.name = self.name.capitalize()
```

This will capitalize the `name` field value before each document insert and replace

And sync and async methods could work as actions.

```python
from beanie import Insert, Replace

class Sample(Document):
    num: int
    name: str

    @after_event([Insert, Replace])
    async def send_callback(self):
        await client.send(self.id)
```