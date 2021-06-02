from uuid import UUID

from tests.odm.models import DocumentWithCustomIdUUID, DocumentWithCustomIdInt


async def test_uuid_id():
    doc = DocumentWithCustomIdUUID(name="TEST")
    await doc.insert()
    new_doc = await DocumentWithCustomIdUUID.get(doc.id)
    assert type(new_doc.id) == UUID


async def test_integer_id():
    doc = DocumentWithCustomIdInt(name="TEST", id=1)
    await doc.insert()
    new_doc = await DocumentWithCustomIdInt.get(doc.id)
    assert type(new_doc.id) == int
