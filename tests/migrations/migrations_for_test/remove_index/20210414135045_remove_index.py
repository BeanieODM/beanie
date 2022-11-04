from pydantic.main import BaseModel

from beanie import Document, iterative_migration


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
        indexes = [
            "_id",
        ]


class Forward:
    @iterative_migration()
    async def name_to_title(
        self, input_document: OldNote, output_document: Note
    ):
        ...


class Backward:
    @iterative_migration()
    async def title_to_name(
        self, input_document: Note, output_document: OldNote
    ):
        ...
