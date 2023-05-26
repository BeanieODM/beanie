import pytest
from pydantic.main import BaseModel

from beanie import init_beanie
from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.migrations.models import RunningDirections
from beanie.odm.documents import Document


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
    for i in range(1, 8):
        note = Note(title=str(i), tag=Tag(name="test", color="red"))
        await note.insert()
    yield i
    await Note.delete_all()


async def test_migration_by_one(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=1,
    )

    await init_beanie(database=db, document_models=[Note])

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "four", "five", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    await run_migrate(migration_settings)

    migration_settings.direction = RunningDirections.BACKWARD

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "four", "five", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)


async def test_migration_by_two(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=2,
    )

    await init_beanie(database=db, document_models=[Note])

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    await run_migrate(migration_settings)

    migration_settings.direction = RunningDirections.BACKWARD

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)


async def test_migration_by_10(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=10,
    )

    await init_beanie(database=db, document_models=[Note])

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    migration_settings.direction = RunningDirections.BACKWARD

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]


async def test_migration_all(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
    )

    await init_beanie(database=db, document_models=[Note])

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    migration_settings.direction = RunningDirections.BACKWARD

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    await run_migrate(migration_settings)
    async for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]
