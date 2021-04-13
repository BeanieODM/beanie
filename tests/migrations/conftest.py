import motor
import pytest
from pydantic import BaseSettings

from beanie import init_beanie
from beanie.migrations.models import MigrationLog


class Settings(BaseSettings):
    mongodb_dsn: str
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
async def db(settings, loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    return client["beanie_db"]


@pytest.fixture(autouse=True)
async def init(db, loop):
    await init_beanie(
        database=db,
        document_models=[
            MigrationLog,
        ],
    )


@pytest.fixture(autouse=True)
async def remove_migrations_log(db, init, loop):
    await MigrationLog.delete_all()
