![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)

[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python ODM for MongoDB, based on [Motor](https://motor.readthedocs.io/en/stable/)
and [Pydantic](https://pydantic-docs.helpmanual.io/).

It uses an abstraction over Pydantic models and Motor collections to work with the database. Class **Document** allows to: create, replace, update, get, find and aggregate.

Beanie supports migrations out of the box.

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

### Materials

#### ODM
- **[Tutorial](https://roman-right.github.io/beanie/tutorial/odm/)** - ODM usage examples
- **[Documentation](https://roman-right.github.io/beanie/documentation/odm/)** - Full list of the ODM classes and
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

### Resources

- **[GitHub](https://github.com/roman-right/beanie)** - GitHub page of the project
- **[Changelog](https://roman-right.github.io/beanie/changelog)** - list of all the valuable changes
- **[Discord](https://discord.gg/ZTTnM7rMaz)** - ask your questions, share ideas or just say `Hello!!`