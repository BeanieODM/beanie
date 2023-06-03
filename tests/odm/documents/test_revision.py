import pytest

from beanie import BulkWriter
from beanie.exceptions import RevisionIdWasChanged
from beanie.odm.operators.update.general import Inc
from tests.odm.models import DocumentWithRevisionTurnedOn
from pymongo.errors import BulkWriteError


async def test_replace():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    doc.num_1 = 2
    await doc.replace()

    doc.num_2 = 3
    await doc.replace()

    for i in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.replace()

    doc._previous_revision_id = "wrong"
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

    for i in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        await found_doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    doc._previous_revision_id = "wrong"
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

    for i in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.save_changes()

    doc._previous_revision_id = "wrong"
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

    for i in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        await found_doc.save()

    doc._previous_revision_id = "wrong"
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

    for i in range(5):
        found_doc = await DocumentWithRevisionTurnedOn.get(doc.id)
        found_doc.num_1 += 1
        async with BulkWriter() as bulk_writer:
            await found_doc.save(bulk_writer=bulk_writer)

    doc._previous_revision_id = "wrong"
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
    old_revision = doc._previous_revision_id

    await doc.save_changes()
    assert doc.revision_id == revision
    assert doc._previous_revision_id == old_revision

    doc = await DocumentWithRevisionTurnedOn.get(doc.id)
    assert doc._previous_revision_id == old_revision
