import pytest
from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str
    mongodb_db_name: str = "beanie_db"
    migrations_path: str = "tests/migrations/migrations_for_tests/"


@pytest.fixture
def settings():
    return Settings()
