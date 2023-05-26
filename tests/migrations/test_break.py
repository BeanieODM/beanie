import pytest
from pydantic.main import BaseModel

from beanie import init_beanie, Indexed
from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.odm.documents import Document
from beanie.odm.models import InspectionStatuses


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    name: Indexed(str, unique=True)
    tag: Tag

    class Settings:
        name = "notes"


class Note(Document):
    name: Indexed(str, unique=True)
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
    await OldNote.get_motor_collection().drop()
    await OldNote.get_motor_collection().drop_indexes()


async def test_migration_break(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/break",
    )
    with pytest.raises(Exception):
        await run_migrate(migration_settings)

    await init_beanie(database=db, document_models=[OldNote])
    inspection = await OldNote.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    notes = await OldNote.get_motor_collection().find().to_list(length=100)
    names = set(n["name"] for n in notes)
    assert names == {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    for note in notes:
        assert "title" not in note
