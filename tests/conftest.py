from uuid import uuid4

import motor
import pytest
from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017"
    mongodb_db_name: str = str(uuid4())


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings, loop):
    return motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings, loop):
    return cli[settings.mongodb_db_name]
