from uuid import UUID

from tests.odm_sync.models import (
    SyncDocumentWithCustomIdUUID,
    SyncDocumentWithCustomIdInt,
)


def test_uuid_id():
    doc = SyncDocumentWithCustomIdUUID(name="TEST")
    doc.insert()
    new_doc = SyncDocumentWithCustomIdUUID.get(doc.id).run()
    assert type(new_doc.id) == UUID


def test_integer_id():
    doc = SyncDocumentWithCustomIdInt(name="TEST", id=1)
    doc.insert()
    new_doc = SyncDocumentWithCustomIdInt.get(doc.id).run()
    assert type(new_doc.id) == int
