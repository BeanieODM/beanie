import pytest
from pydantic.main import BaseModel

from beanie import init_beanie
from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.migrations.models import RunningDirections
from beanie.odm.documents import Document
from beanie.odm.models import InspectionStatuses


class Tag(BaseModel):
    color: str
    name: str


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


@pytest.fixture()
async def notes(db):
    await init_beanie(database=db, document_models=[Note])
    await Note.delete_all()
    for i in range(10):
        note = Note(title=str(i), tag=Tag(name="test", color="red"))
        await note.insert()
    yield
    await Note.delete_all()


async def test_migration_change_value(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/change_value",
    )
    await run_migrate(migration_settings)

    await init_beanie(database=db, document_models=[Note])
    inspection = await Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await Note.find_one({"title": "five"})
    assert note is not None

    note = await Note.find_one({"title": "5"})
    assert note is None

    migration_settings.direction = RunningDirections.BACKWARD
    await run_migrate(migration_settings)
    inspection = await Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await Note.find_one({"title": "5"})
    assert note is not None

    note = await Note.find_one({"title": "five"})
    assert note is None
