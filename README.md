[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)](https://github.com/roman-right/beanie)

[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python object-document mapper (ODM) for MongoDB, based on [Motor](https://motor.readthedocs.io/en/stable/) and [Pydantic](https://pydantic-docs.helpmanual.io/).

When using Beanie each database collection has a corresponding `Document` that is used to interact with that collection.
In addition to retrieving data, Beanie allows you to add, update, or delete documents from the collection as well.

Beanie saves you time by removing boiler-plate code and it helps you focus on the parts of your app that actually matter.

Data and schema migrations are supported by Beanie out of the box.

### Installation

#### PIP

```shell
pip install beanie
```

#### Poetry

```shell
poetry add beanie
```

### Quick Start

```python
from typing import Optional, List

import motor
from beanie import Document, init_beanie
from pydantic import BaseModel


class Tag(BaseModel):
    name: str
    color: str


class Note(Document):
    title: str
    text: Optional[str]
    tag_list: List[Tag] = []


async def main():
    # Crete Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017"
    )
    
    # Init beanie with the Note document class
    await init_beanie(database=client.db_name, document_models=[Note])

    # Get all the notes
    all_notes = await Note.find_all().to_list()
```

### Documentation

#### ODM
- **[Tutorial](https://roman-right.github.io/beanie/tutorial/odm/)** - ODM usage examples
- **[API](https://roman-right.github.io/beanie/documentation/odm/)** - Full list of the ODM classes and
  methods with descriptions

#### Migrations
- **[Tutorial](https://roman-right.github.io/beanie/tutorial/odm/)** - Migrations usage examples

### Example Projects

- **[FastAPI Demo](https://github.com/roman-right/beanie-fastapi-demo)** - Beanie and FastAPI collaboration demonstration. CRUD and Aggregation.
- **[Indexes Demo](https://github.com/roman-right/beanie-index-demo)** - Regular and Geo Indexes usage example wrapped to a microservice. 

### Articles

- **[Announcing Beanie - MongoDB ODM](https://dev.to/romanright/announcing-beanie-mongodb-odm-56e)**
- **[Build a Cocktail API with Beanie and MongoDB](https://developer.mongodb.com/article/beanie-odm-fastapi-cocktails/)**
- **[MongoDB indexes with Beanie](https://dev.to/romanright/mongodb-indexes-with-beanie-43e8)**
- **[Beanie Projections. Reducing network and database load.](https://dev.to/romanright/beanie-projections-reducing-network-and-database-load-3bih)**

### Resources

- **[GitHub](https://github.com/roman-right/beanie)** - GitHub page of the project
- **[Changelog](https://roman-right.github.io/beanie/changelog)** - list of all the valuable changes
- **[Discord](https://discord.gg/ZTTnM7rMaz)** - ask your questions, share ideas or just say `Hello!!`

----
Supported by [JetBrains](https://jb.gg/OpenSource)

[![JetBrains](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/jetbrains.svg)](https://jb.gg/OpenSource)
