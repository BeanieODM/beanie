import pytest

from beanie.exceptions import RevisionIdWasChanged
from tests.odm.models import DocumentWithRevisionTurnedOn


async def test_replace():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    doc.num_1 = 2
    await doc.replace()

    doc.num_2 = 3
    await doc.replace()

    doc._previous_revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        await doc.replace()

    await doc.replace(force=True)


async def test_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    await doc.insert()

    doc.num_1 = 2
    await doc.save_changes()

    doc.num_2 = 3
    await doc.save_changes()

    doc._previous_revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        await doc.save_changes()

    await doc.save_changes(force=True)
