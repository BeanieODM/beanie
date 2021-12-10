# Relations

The document can contain links to other documents in their fields.

*Only top-level fields are fully supported for now.*

The next field types are supported:

- `Link[...]`
- `Optional[Link[...]]`
- `List[Link[...]]`

Direct link to the document:

```python
from beanie import Document, Link

class Door(Document):
    height: int = 2
    width: int = 1


class House(Document):
    name: str
    door: Link[Door]
```

Optional direct link to the document:

```python
from typing import Optional

from beanie import Document, Link

class Door(Document):
    height: int = 2
    width: int = 1


class House(Document):
    name: str
    door: Optional[Link[Door]]
```

List of the links:

```python
from typing import List

from beanie import Document, Link

class Window(Document):
    x: int = 10
    y: int = 10


class House(Document):
    name: str
    door: Link[Door]
    windows: List[Link[Window]]
```

Other link patterns are not supported for now. If you need something more specific for your use-case, please leave an issue on the GitHub page - <https://github.com/roman-right/beanie>

## Write

The next write methods support relations:

- `insert(...)`
- `replace(...)`
- `save(...)`

To apply the writing method to the linked documents, you should set the respective `link_rule` parameter

```python
house.windows = [Window(x=100, y=100)]
house.name = "NEW NAME"

# The next call will insert a new window object and replace the house instance with updated data
await house.save(link_rule=WriteRules.WRITE)

# `insert` and `replace` methods will work the same way
```

Or Beanie can ignore internal links with the `link_rule` parameter `WriteRules.DO_NOTHING`

```python
house.door.height = 3
house.name = "NEW NAME"

# The next call will just replace the house instance with new data, but the linked door object will not be synced
await house.replace(link_rule=WriteRules.DO_NOTHING)

# `insert` and `save` methods will work the same way
```

## Fetch

### Prefetch

You can fetch linked documents on the find query step, using the parameter `fetch_links`

```python
houses = await House.find(
    House.name == "test", 
    fetch_links=True
).to_list()
```

All the find methods supported:
- find
- find_one
- get

Beanie uses a single aggregation query under the hood to fetch all the linked documents. This operation is very effective.

If a direct link is referred to a non-existent document, after the fetching it will stay the object of the `Link` class.

Fetching will ignore non-existent documents for the list of links fields.

### On-demand fetch

If you don't use prefetching, linked documents will be presented as objects of the `Link` class. You can fetch them manually then.
To fetch all the linked documents you can use the `fetch_all_links` method

```python
await house.fetch_all_links()
```

It will fetch all the linked documents and replace `Link` objects with them.

Or you can fetch a single field:

```python
await house.fetch_link(House.door)
```

This will fetch the Door object and put it in the `door` field of the `house` object.

## Delete

Delete method works the same way as write operations, but it uses other rules:

To delete all the links on the document deletion you should use the `DeleteRules.DELETE_LINKS` value for the `link_rule` parameter

```python
await house.delete(link_rule=DeleteRules.DELETE_LINKS)
```

To keep linked documents you can use the `DO_NOTHING` rule

```python
await house.delete(link_rule=DeleteRules.DO_NOTHING)
```
