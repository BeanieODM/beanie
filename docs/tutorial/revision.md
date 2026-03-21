# Revision

## What is Revision?

The revision feature protects against **lost updates** in concurrent
environments.  Each document stores a `revision_id` (a UUID) that changes on
every write.  Before Beanie writes a change, it checks that the local
`revision_id` still matches the one in the database.  If another process
updated the document in the meantime, the IDs will differ and Beanie raises
`RevisionIdWasChanged` — preventing one write from silently overwriting
another.

```
Process A reads doc   →  revision_id = "abc"
Process B reads doc   →  revision_id = "abc"

Process A writes doc  →  revision_id becomes "xyz"

Process B tries to write  →  local "abc" ≠ DB "xyz"  →  RevisionIdWasChanged 🛑
```

---

## Enabling Revision

Set `use_revision = True` in the document's `Settings` class:

```python
from beanie import Document


class BankAccount(Document):
    owner: str
    balance: float

    class Settings:
        name = "bank_accounts"
        use_revision = True
```

---

## Basic Usage

Once enabled, all mutating operations (`save`, `replace`, `save_changes`,
`update`) automatically check and update `revision_id`:

```python
account = await BankAccount.find_one(BankAccount.owner == "Alice")
account.balance += 100.0

# Succeeds if no other process has modified the document since we read it
await account.save()
```

If a concurrent process modifies the document between our read and our write:

```python
from beanie.exceptions import RevisionIdWasChanged

try:
    await account.replace()
except RevisionIdWasChanged:
    # Re-fetch the latest version and retry or notify the user
    account = await BankAccount.find_one(BankAccount.owner == "Alice")
    account.balance += 100.0
    await account.replace()
```

---

## Ignoring Revision (Force Write)

If you want to overwrite the document regardless of concurrent changes — for
example in an administrative "last write wins" scenario — pass
`ignore_revision=True`:

```python
await account.replace(ignore_revision=True)
```

> Use this sparingly.  It disables the concurrency protection and can cause
> data loss.

---

## Retry Pattern

A simple retry loop for optimistic concurrency:

```python
import asyncio
from beanie.exceptions import RevisionIdWasChanged

MAX_RETRIES = 3


async def credit(owner: str, amount: float) -> None:
    for attempt in range(MAX_RETRIES):
        account = await BankAccount.find_one(BankAccount.owner == owner)
        if account is None:
            raise ValueError(f"Account for {owner} not found")
        account.balance += amount
        try:
            await account.save()
            return
        except RevisionIdWasChanged:
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(0.05 * (attempt + 1))  # brief back-off
```

---

## How `revision_id` is Stored

The `revision_id` field is a UUID stored in the MongoDB document but excluded
from Pydantic's public model output (`exclude=True`).  It is managed entirely
by Beanie and should not be set manually.

When a write succeeds, the new `revision_id` is written back to the in-memory
instance automatically, so subsequent saves from the same object will use the
updated token.

---

## Interaction with BulkWriter

> **Warning:** The revision feature may work incorrectly with `BulkWriter`.

`BulkWriter` collects operations and sends them in a single batch, which
prevents per-document revision checking.  Avoid combining `use_revision = True`
with `BulkWriter` unless you are certain about the concurrency implications.

---

## Summary

| Scenario | Behaviour |
|---|---|
| Concurrent write detected | `RevisionIdWasChanged` raised |
| Force-write without check | Pass `ignore_revision=True` |
| `BulkWriter` + revision | Not reliably supported |
| Revision stored as | `UUID` in `revision_id` field (excluded from schema) |
