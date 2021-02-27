import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from beanie import Document
from tests.models import DocumentTestModelWithCustomCollection


async def test_init():
    class NewDocument(Document):
        test_str: str

    with pytest.raises(AttributeError):
        NewDocument(test_str="test")


async def test_custom_collection():
    collection: AsyncIOMotorCollection = (
        DocumentTestModelWithCustomCollection.collection()
    )
    assert collection.name == "custom"
