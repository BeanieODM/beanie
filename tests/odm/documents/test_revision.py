import pytest
from pymongo.errors import BulkWriteError, DuplicateKeyError

from beanie import BulkWriter
from beanie.exceptions import RevisionIdWasChanged
from beanie.odm.operators.update.general import Inc
from tests.odm.models import (
    DocumentWithRevisionAndUniqueField,
    DocumentWithRevisionTurnedOn,
    LockWithRevision,
    WindowWithRevision,
)


async def test_replace():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    doc.num_1 = 2
    await doc.replace()

    doc.num_2 = 3
    await doc.replace()

    for _ in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.replace()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        await doc.replace()

    await doc.replace(ignore_revision=True)
    await doc.replace()


async def test_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)

    await doc.insert()

    await doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))
    await doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    for _ in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        await found_doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    doc.revision_id = "wrong"
    with pytest.raises(RevisionIdWasChanged):
        await doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    await doc.update(
        Inc({DocumentWithRevisionTurnedOn.num_1: 1}), ignore_revision=True
    )
    await doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))


async def test_save_changes():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    doc.num_1 = 2
    await doc.save_changes()

    doc.num_2 = 3
    await doc.save_changes()

    for _ in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.save_changes()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        await doc.save_changes()

    await doc.save_changes(ignore_revision=True)
    await doc.save_changes()


async def test_save():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)

    doc.num_1 = 2
    await doc.save()

    doc.num_2 = 3
    await doc.save()

    for _ in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.save()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        await doc.save()

    await doc.save(ignore_revision=True)
    await doc.save()


async def test_update_bulk_writer():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.save()

    doc.num_1 = 2
    async with BulkWriter() as bulk_writer:
        await doc.save(bulk_writer=bulk_writer)

    doc = await DocumentWithRevisionTurnedOn.get(doc.id)

    doc.num_2 = 3
    async with BulkWriter() as bulk_writer:
        await doc.save(bulk_writer=bulk_writer)

    doc = await DocumentWithRevisionTurnedOn.get(doc.id)

    for _ in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        async with BulkWriter() as bulk_writer:
            await found_doc.save(bulk_writer=bulk_writer)

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(BulkWriteError):
        async with BulkWriter() as bulk_writer:
            await doc.save(bulk_writer=bulk_writer)

    async with BulkWriter() as bulk_writer:
        await doc.save(bulk_writer=bulk_writer, ignore_revision=True)


async def test_empty_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    # This fails with RevisionIdWasChanged
    await doc.update({"$set": {"num_1": 1}})


async def test_save_changes_when_there_were_no_changes():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()
    revision = doc.revision_id

    await doc.save_changes()
    assert doc.revision_id == revision

    await DocumentWithRevisionTurnedOn.get(doc.id)
    assert doc.revision_id == revision


async def test_revision_id_for_link():
    lock = LockWithRevision(k=1)
    await lock.insert()

    lock_rev_id = lock.revision_id

    window = WindowWithRevision(x=0, y=0, lock=lock)

    await window.insert()
    assert lock.revision_id == lock_rev_id


async def test_duplicate_key_error_on_unique_field_not_converted_to_revision_error():
    """Regression test: a DuplicateKeyError on a user-defined unique index
    should propagate as DuplicateKeyError, not be swallowed and re-raised
    as RevisionIdWasChanged. See issue #1057."""
    doc1 = DocumentWithRevisionAndUniqueField(
        num_1=1, num_2=2, unique_field="unique_value"
    )
    await doc1.insert()

    doc2 = DocumentWithRevisionAndUniqueField(
        num_1=3, num_2=4, unique_field="unique_value"
    )
    with pytest.raises(DuplicateKeyError):
        await doc2.insert()


async def test_save_duplicate_unique_field_raises_duplicate_key_error():
    """Regression test: calling save() on a document whose unique field
    collides with an existing document should raise DuplicateKeyError,
    not RevisionIdWasChanged. See issue #1057."""
    doc1 = DocumentWithRevisionAndUniqueField(
        num_1=1, num_2=2, unique_field="save_unique"
    )
    await doc1.save()

    doc2 = DocumentWithRevisionAndUniqueField(
        num_1=3, num_2=4, unique_field="save_unique"
    )
    with pytest.raises(DuplicateKeyError):
        await doc2.save()


async def test_update_duplicate_unique_field_raises_duplicate_key_error():
    """Regression test: updating a field to a value that violates a unique
    constraint should raise DuplicateKeyError, not RevisionIdWasChanged.
    See issue #1057."""
    doc1 = DocumentWithRevisionAndUniqueField(
        num_1=1, num_2=2, unique_field="update_val_a"
    )
    await doc1.insert()

    doc2 = DocumentWithRevisionAndUniqueField(
        num_1=3, num_2=4, unique_field="update_val_b"
    )
    await doc2.insert()

    doc2.unique_field = "update_val_a"
    with pytest.raises(DuplicateKeyError):
        await doc2.save()


async def test_revision_conflict_still_raises_revision_error():
    """Ensure that actual revision conflicts still raise
    RevisionIdWasChanged after the DuplicateKeyError fix."""
    doc = DocumentWithRevisionAndUniqueField(
        num_1=1, num_2=2, unique_field="rev_conflict"
    )
    await doc.insert()

    stale = await DocumentWithRevisionAndUniqueField.get(doc.id)
    doc.num_1 = 10
    await doc.save()

    stale.num_1 = 20
    with pytest.raises(RevisionIdWasChanged):
        await stale.save()
