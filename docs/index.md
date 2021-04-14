![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)

[Beanie](https://github.com/roman-right/beanie) - is an asynchronous ODM for MongoDB, based on [Motor](https://motor.readthedocs.io/en/stable/)
and [Pydantic](https://pydantic-docs.helpmanual.io/).

It uses an abstraction over Pydantic models and Motor collections to work with the database. Class Document allows to
create, replace, update, get, find and aggregate.

## Installation

### PIP

```shell
pip install beanie
```

### Poetry

```shell
poetry add beanie
```

## Quick Start

- [ODM](quickstart/odm/)
- [Migrations](quickstart/migrations)