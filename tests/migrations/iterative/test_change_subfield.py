import os

import pytest
from pydantic.main import BaseModel

from beanie import init_beanie
from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.migrations.models import RunningDirections
from beanie.odm.documents import Document
from beanie.odm.models import InspectionStatuses


class OldTag(BaseModel):
    color: str
    name: str


class Tag(BaseModel):
    color: str
    title: str


class OldNote(Document):
    title: str
    tag: OldTag

    class Collection:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Collection:
        name = "notes"


@pytest.fixture()
async def notes(loop, db):
    await init_beanie(database=db, document_models=[OldNote])
    await OldNote.delete_all()
    for i in range(10):
        note = OldNote(title=str(i), tag=OldTag(name="test", color="red"))
        await note.create()
    yield
    await OldNote.delete_all()


async def test_migration_change_subfield_value(settings, notes, db):
    os.chdir("/home/ro/Projects/Pet/beanie")  # TODO fix this
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/change_subfield",
    )
    await run_migrate(migration_settings)

    await init_beanie(database=db, document_models=[Note])
    inspection = await Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await Note.find_one({})
    assert note.tag.title == "test"

    migration_settings.direction = RunningDirections.BACKWARD
    await run_migrate(migration_settings)
    inspection = await OldNote.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = await OldNote.find_one({})
    assert note.tag.name == "test"
