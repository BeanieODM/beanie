from uuid import UUID

from tests.sync.models import (
    DocumentWithCustomIdUUID,
    DocumentWithCustomIdInt,
)


def test_uuid_id():
    doc = DocumentWithCustomIdUUID(name="TEST")
    doc.insert()
    new_doc = DocumentWithCustomIdUUID.get(doc.id).run()
    assert type(new_doc.id) == UUID


def test_integer_id():
    doc = DocumentWithCustomIdInt(name="TEST", id=1)
    doc.insert()
    new_doc = DocumentWithCustomIdInt.get(doc.id).run()
    assert type(new_doc.id) == int
