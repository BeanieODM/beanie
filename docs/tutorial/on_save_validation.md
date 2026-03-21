# On-Save Validation

## Overview

Pydantic supports `validate_assignment = True` in its model config, which
validates every field assignment immediately.  This is convenient but adds
overhead on every attribute write, which can be expensive in hot paths.

Beanie provides an alternative: **validate on save**.  Validation runs once,
just before the document is persisted to MongoDB (`insert`, `replace`, `save`,
`save_changes`), rather than on every field assignment.

## Enabling Validate-on-Save

Set `validate_on_save = True` inside the document's `Settings` class:

```python
from beanie import Document


class Product(Document):
    name: str
    price: float
    stock: int = 0

    class Settings:
        name = "products"
        validate_on_save = True
```

## How It Works

When any write operation is called, Beanie re-parses the document through
Pydantic before sending it to MongoDB.  If any field has an invalid value at
that point, a `ValidationError` is raised and the write is aborted.

```python
product = await Product.find_one(Product.name == "Widget")
product.price = "not-a-number"   # no error yet

# ValidationError raised here — nothing is written to the database
await product.save()
```

## Catching Validation Errors

```python
from pydantic import ValidationError


product = await Product.find_one(Product.name == "Widget")
product.stock = -5               # invalid value

try:
    await product.replace()
except ValidationError as e:
    print(e)
    # Handle or log the error; the document is unchanged in the DB
```

## Using Custom Pydantic Validators

`validate_on_save` is fully compatible with Pydantic field validators and model
validators.  They run as part of the re-parse step:

```python
from pydantic import field_validator, model_validator
from beanie import Document


class Order(Document):
    quantity: int
    unit_price: float
    total: float = 0.0

    class Settings:
        name = "orders"
        validate_on_save = True

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than zero")
        return v

    @model_validator(mode="after")
    def compute_total(self) -> "Order":
        self.total = self.quantity * self.unit_price
        return self


order = Order(quantity=3, unit_price=9.99)
await order.insert()             # total is computed and validated on insert

order.quantity = 0
await order.save()               # raises ValidationError: quantity must be > 0
```

## Triggering Validation Without Saving

You can run the full validation pass manually without persisting the document:

```python
await product.validate_self()
```

This fires `before_event(ValidateOnSave)` / `after_event(ValidateOnSave)`
hooks and re-parses the document, but does not write anything to the database.

## Validate-on-Save vs. `validate_assignment`

| Feature | `validate_assignment = True` | `validate_on_save = True` |
|---|---|---|
| When validation runs | On every field assignment | Only before a write operation |
| Performance cost | Per-assignment | Per-write |
| Catches errors | Immediately on assignment | At write time |
| Works with `save_changes()` | Yes | Yes |
| Works with bulk writes | Limited | Yes |

Use `validate_on_save` when you want the safety of full validation before
persistence without paying the per-assignment cost.  Use `validate_assignment`
when you want immediate feedback on every field change (e.g. in interactive
forms or API request models).
