import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic_settings import BaseSettings
else:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/beanie_db"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings):
    client = AsyncIOMotorClient(settings.mongodb_dsn)

    yield client

    client.close()


@pytest.fixture()
def db(cli, settings):
    return cli[settings.mongodb_db_name]
