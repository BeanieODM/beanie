![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg)

[Beanie](https://github.com/roman-right/beanie) - is an asynchronous ODM for MongoDB, based on [Motor](https://motor.readthedocs.io/en/stable/)
and [Pydantic](https://pydantic-docs.helpmanual.io/).

It uses an abstraction over Pydantic models and Motor collections to work with the database. Class Document allows to
create, replace, update, get, find and aggregate.

## Installation

##### Stable

```shell
pip install beanie
```

##### Beta with migrations

```shell
pip install beanie==0.4.b1
```

#### Poetry

##### Stable

```shell
poetry add beanie
```

##### Beta with migrations

```shell
poetry add beanie==0.4.b1
```


## Quick Start

- [ODM](quickstart/odm/)
- [Migrations](quickstart/migrations)