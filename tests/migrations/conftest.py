import pytest

from beanie import init_beanie
from beanie.migrations.models import MigrationLog


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
