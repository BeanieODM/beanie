import pytest
from pymongo.errors import BulkWriteError

from beanie import BulkWriter
from beanie.exceptions import RevisionIdWasChanged
from beanie.odm.operators.update.general import Inc
from tests.odm.models import (
    DocumentWithRevisionTurnedOn,
    LockWithRevision,
    WindowWithRevision,
)


async def test_insert():
    doc_on_beanie = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc_on_beanie.insert()
    doc_on_db = await DocumentWithRevisionTurnedOn.get(doc_on_beanie.id)
    if not doc_on_db:
        raise Exception
    assert doc_on_beanie.revision_id == doc_on_db.revision_id


#   -----------------------------------------------------------------------
#   This test fails as below

# >       assert doc_on_beanie.revision_id == doc_on_db.revision_id
# E       AssertionError: assert UUID('7bbbbebd-04d0-417f-b4cc-4c96dd9812a2') == None
# E        +  where UUID('7bbbbebd-04d0-417f-b4cc-4c96dd9812a2') = DocumentWithRevisionTurnedOn(id=ObjectId('6865e5875dddb4f1219557d3'), revision_id=UUID('7bbbbebd-04d0-417f-b4cc-4c96dd9812a2'), num_1=1, num_2=2).revision_id
# E        +  and   None = DocumentWithRevisionTurnedOn(id=ObjectId('6865e5875dddb4f1219557d3'), revision_id=None, num_1=1, num_2=2).revision_id

#   From this result, we can see that the revision_id is not set when we insert the document
#   -----------------------------------------------------------------------


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

    for i in range(5):
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

    for i in range(5):
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

    for i in range(5):
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

    for i in range(5):
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
