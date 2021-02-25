import motor.motor_asyncio
import pytest
from pydantic import BaseSettings

from beanie.general import init_beanie
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
    init_beanie(database=db, document_models=[DocumentTestModel])
    yield None
    await DocumentTestModel.collection().drop()


@pytest.fixture
def document_not_inserted():
    return DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )


@pytest.fixture
async def document(
        document_not_inserted, loop
) -> DocumentTestModel:
    return await document_not_inserted.create()
