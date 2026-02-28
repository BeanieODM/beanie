import pytest
from pydantic_settings import BaseSettings
from pymongo import AsyncMongoClient


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/beanie_db"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
async def cli(settings):
    client = AsyncMongoClient(settings.mongodb_dsn)

    yield client

    await client.close()


@pytest.fixture
def db(cli, settings):
    return cli[settings.mongodb_db_name]
