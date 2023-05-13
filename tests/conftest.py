import motor.motor_asyncio
import pytest
from pydantic import BaseSettings

from beanie.odm.utils.general import DatabaseVersion


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/beanie_db"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings, loop):
    return motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings, loop):
    return cli[settings.mongodb_db_name]


@pytest.fixture()
async def database_version(db):
    build_info = await db.command({"buildInfo": 1})
    return DatabaseVersion.from_str(build_info["version"])
