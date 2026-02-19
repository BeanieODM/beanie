# ODM Client

The `ODMClient` is a high-level utility for managing MongoDB connections and initializing multiple databases with Beanie models in a centralized way. It is especially useful for applications that need to interact with multiple databases or want a structured way to handle migrations and initialization.

## Initialization

You can initialize the `ODMClient` by providing a MongoDB connection URI and optional keyword arguments for the underlying `AsyncMongoClient`.

```python
from beanie import ODMClient

uri = "mongodb://localhost:27017"
client = ODMClient(uri)
```

## Registering Databases

The `register_database` method allows you to initialize Beanie for a specific database with a list of document models.

```python
from beanie import Document

class User(Document):
    name: str

async def init():
    await client.register_database(
        db_name="user_db",
        models=[User],
        allow_index_dropping=False
    )
```

### Multiple Databases at Once

The `init_db` method allows you to initialize multiple databases from a configuration dictionary.

```python
class Product(Document):
    title: str

db_config = {
    "user_db": [User],
    "product_db": [Product]
}

async def init_all():
    await client.init_db(db_config)
```

## Migrations

`ODMClient` supports running migrations during database registration. If a `migrations_path` is provided, Beanie will run migrations for the specified database before initializing the models.

```python
await client.register_database(
    db_name="app_db",
    models=[User],
    migrations_path="path/to/migrations"
)
```

## Async Context Manager

`ODMClient` can be used as an async context manager to ensure that the MongoDB connection is properly closed when the application exits.

```python
async with ODMClient(uri) as client:
    await client.init_db(db_config)
    # ... use the client ...
# Connection is closed automatically here
```

## Important Note: Global Model Binding

Beanie binds document models to a database **globally**. If you register the same model class in multiple databases using `ODMClient`, the **last** registration will prevail for that class across your entire application.

```python
# User model will be bound to "db_one"
await client.register_database("db_one", [User])

# User model will now be bound to "db_two" globally
await client.register_database("db_two", [User])
```
