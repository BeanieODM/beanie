import pytest
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from beanie.odm.client import ODMClient
from beanie.odm.documents import Document


class SampleDoc(Document):
    name: str


class AnotherDoc(Document):
    title: str


@pytest.fixture
async def odm_client():
    # Use a test database URI.
    uri = "mongodb://localhost:27017"
    client = ODMClient(uri)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_odm_client_init(odm_client):
    assert isinstance(odm_client.client, AsyncMongoClient)
    assert odm_client.databases == {}


@pytest.mark.asyncio
async def test_odm_client_register_database(odm_client):
    db_name = "test_odm_client_db"
    models = [SampleDoc]

    await odm_client.register_database(db_name, models)

    assert db_name in odm_client.databases
    assert isinstance(odm_client.get_database(db_name), AsyncDatabase)

    # Verify beanie was initialized for the model
    # We can check if the collection is set
    assert SampleDoc.get_pymongo_collection() is not None
    assert SampleDoc.get_pymongo_collection().name == "SampleDoc"

    # Cleanup
    await odm_client.client.drop_database(db_name)


@pytest.mark.asyncio
async def test_odm_client_init_db(odm_client):
    db_config = {"db1": [SampleDoc], "db2": [AnotherDoc]}

    await odm_client.init_db(db_config)

    assert "db1" in odm_client.databases
    assert "db2" in odm_client.databases

    assert SampleDoc.get_pymongo_collection().database.name == "db1"
    assert AnotherDoc.get_pymongo_collection().database.name == "db2"

    await odm_client.client.drop_database("db1")
    await odm_client.client.drop_database("db2")


@pytest.mark.asyncio
async def test_odm_client_context_manager():
    uri = "mongodb://localhost:27017"
    async with ODMClient(uri) as client:
        assert isinstance(client, ODMClient)
        assert client.client is not None

    # Client should be closed
