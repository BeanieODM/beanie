import pytest
from pymongo import AsyncMongoClient

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


@pytest.fixture
async def cli(settings):
    async with AsyncMongoClient(settings.mongodb_dsn) as client:
        yield client


@pytest.fixture
def db(cli, settings):
    return cli[settings.mongodb_db_name]
