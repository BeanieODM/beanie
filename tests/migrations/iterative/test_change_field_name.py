import motor
import pytest
from click.testing import CliRunner
from pydantic.main import BaseModel

from beanie import init_beanie
from beanie.odm.documents import Document
from beanie.executors.migrate import migrate


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    name: str
    tag: Tag

    class Collection:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Collection:
        name = "notes"


@pytest.fixture()
def db(settings):
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    return client["beanie_db"]


@pytest.fixture()
async def notes(loop, db):
    await init_beanie(database=db, document_models=[OldNote])
    for i in range(10):
        note = OldNote(name=str(i), tag=Tag(name="test", color="red"))
        await note.create()
    yield
    # await Note.delete_all()


def test_migration_change_field_name(settings, notes):
    runner = CliRunner()
    result = runner.invoke(
        migrate,
        [
            "-uri",
            settings.mongodb_dsn,
            "-db",
            settings.mongodb_db_name,
            "--path",
            settings.migrations_path,
        ],
    )
    assert result.output == 1
