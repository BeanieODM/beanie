import motor.motor_asyncio
import pytest
from pydantic import BaseSettings

from beanie import Collection
from tests.models import DocumentTestModel, SubDocument

object_storage = {}


class Settings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_user: str = "beanie"
    mongo_pass: str = "beanie"
    mongo_db: str = "beanie_db"

    @property
    def mongo_dsn(self):
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_pass}"
            f"@{self.mongo_host}:27017/{self.mongo_db}"
        )


@pytest.fixture(autouse=True)
async def init(loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        Settings().mongo_dsn, serverSelectionTimeoutMS=100
    )
    db = client.beanie_db
    test_collection = Collection(
        name="test_collection", db=db, document_model=DocumentTestModel
    )
    object_storage["collection"] = test_collection
    yield None
    await test_collection.motor_collection.drop()


@pytest.fixture
def collection():
    return object_storage["collection"]


@pytest.fixture
def document_not_inserted():
    return DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )


@pytest.fixture
async def document(
    document_not_inserted, collection, loop
) -> DocumentTestModel:
    document = await collection.insert_one(document_not_inserted)
    return document
