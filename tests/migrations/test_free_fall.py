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


class OldNote(Document):
    name: str
    tag: Tag

    class Settings:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


@pytest.fixture()
async def notes(db):
    await init_beanie(database=db, document_models=[OldNote])
    await OldNote.delete_all()
    for i in range(10):
        note = OldNote(name=str(i), tag=Tag(name="test", color="red"))
        await note.insert()
    yield
    await OldNote.delete_all()


async def test_migration_free_fall(settings, notes, db):
    if not db.client.is_mongos and not len(db.client.nodes) > 1:
        return pytest.skip(
            "MongoDB server does not support transactions as it is neighter a mongos instance not a replica set."
        )

    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/free_fall",
    )
    await run_migrate(migration_settings)

    await init_beanie(database=db, document_models=[Note])
    inspection = await Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await Note.find_one({})
    assert note.title == "0"

    migration_settings.direction = RunningDirections.BACKWARD
    await run_migrate(migration_settings)
    inspection = await OldNote.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await OldNote.find_one({})
    assert note.name == "0"
