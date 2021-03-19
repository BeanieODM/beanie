from typing import List

import motor

from beanie import init_beanie, Document
from tests.conftest import Settings
from tests.models import SubDocument


async def test_document_meta():
    class DocumentTestModelWithDocumentMetaClass(Document):
        test_int: int
        test_list: List[SubDocument]
        test_str: str

        class DocumentMeta:
            collection_name = "custom_name"

    client = motor.motor_asyncio.AsyncIOMotorClient(
        Settings().mongo_dsn, serverSelectionTimeoutMS=100
    )
    db = client.beanie_db
    await init_beanie(
        database=db,
        document_models=[DocumentTestModelWithDocumentMetaClass],
    )
    collection = DocumentTestModelWithDocumentMetaClass.get_motor_collection()
    assert collection.name == "custom_name"
    await DocumentTestModelWithDocumentMetaClass.get_motor_collection().drop()
