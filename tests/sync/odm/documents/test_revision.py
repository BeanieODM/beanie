import pytest

from beanie.exceptions import RevisionIdWasChanged
from tests.sync.models import DocumentWithRevisionTurnedOn


def test_replace():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    doc.num_1 = 2
    doc.replace()

    doc.num_2 = 3
    doc.replace()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        found_doc.replace()

    doc._previous_revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        doc.replace()

    doc.replace(ignore_revision=True)


def test_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    doc.num_1 = 2
    doc.save_changes()

    doc.num_2 = 3
    doc.save_changes()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        found_doc.save_changes()

    doc._previous_revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        doc.save_changes()

    doc.save_changes(ignore_revision=True)


def test_empty_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    # This fails with RevisionIdWasChanged
    doc.update({"$set": {"num_1": 1}})
