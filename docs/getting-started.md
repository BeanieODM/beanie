# Getting started

## Installing beanie

You can simply install Beanie from the [PyPI](https://pypi.org/project/beanie/):

### PIP

```shell
pip install beanie
```

### Poetry

```shell
poetry add beanie
```
### Uv

```shell
uv add beanie
```

### Optional dependencies

Beanie supports some optional dependencies from PyMongo (`pip`, `poetry` or `uv` can be used).

GSSAPI authentication requires `gssapi` extra dependency:

```bash
pip install "beanie[gssapi]"
```

MONGODB-AWS authentication requires `aws` extra dependency:

```bash
pip install "beanie[aws]"
```

Support for mongodb+srv:// URIs requires `srv` extra dependency:

```bash
pip install "beanie[srv]"
```

OCSP requires `ocsp` extra dependency:

```bash
pip install "beanie[ocsp]"
```

Wire protocol compression with snappy requires `snappy` extra
dependency:

```bash
pip install "beanie[snappy]"
```

Wire protocol compression with zstandard requires `zstd` extra
dependency:

```bash
pip install "beanie[zstd]"
```

Client-Side Field Level Encryption requires `encryption` extra
dependency:

```bash
pip install "beanie[encryption]"
```

You can install all dependencies automatically with the following
command:

```bash
pip install "beanie[gssapi,aws,ocsp,snappy,srv,zstd,encryption]"
```

## Initialization

Getting Beanie setup in your code is really easy:

1.  Write your database model as a Pydantic class but use `beanie.Document` instead of `pydantic.BaseModel`.
2.  Initialize Async PyMongo, as Beanie uses this as an async database engine under the hood.
3.  Call `beanie.init_beanie` with the PyMongo client and list of Beanie models

The code below should get you started and shows some of the field types that you can use with beanie.

```python
from typing import Optional

from pymongo import AsyncMongoClient
from pydantic import BaseModel

from beanie import Document, Indexed, init_beanie


class Category(BaseModel):
    name: str
    description: str


# This is the model that will be saved to the database
class Product(Document):
    name: str                          # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(float)              # You can also specify that a field should correspond to an index
    category: Category                 # You can include pydantic models as well


# Call this from within your event loop to get beanie setup.
async def init():
    # Create Async PyMongo client
    client = AsyncMongoClient("mongodb://user:pass@host:27017")

    # Init beanie with the Product document class
    await init_beanie(database=client.db_name, document_models=[Product])
```
