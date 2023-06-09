import pytest
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic.main import BaseModel

from beanie import init_beanie
from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.odm.documents import Document


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"
        indexes = ["title"]


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
        note = OldNote(title=str(i), tag=Tag(name="test", color="red"))
        await note.insert()
    yield
    await OldNote.delete_all()


async def test_remove_index_allowed(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
        allow_index_dropping=True,
    )
    await run_migrate(migration_settings)

    await init_beanie(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: AsyncIOMotorCollection = Note.get_motor_collection()
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
    }


async def test_remove_index_default(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
    )
    await run_migrate(migration_settings)

    await init_beanie(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: AsyncIOMotorCollection = Note.get_motor_collection()
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "title_1": {"key": [("title", 1)], "v": 2},
    }


async def test_remove_index_not_allowed(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
        allow_index_dropping=False,
    )
    await run_migrate(migration_settings)

    await init_beanie(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: AsyncIOMotorCollection = Note.get_motor_collection()
    index_info = await collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "title_1": {"key": [("title", 1)], "v": 2},
    }
