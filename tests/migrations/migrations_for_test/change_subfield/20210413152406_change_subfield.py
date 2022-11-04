from pydantic.main import BaseModel

from beanie import Document, iterative_migration


class OldTag(BaseModel):
    color: str
    name: str


class Tag(BaseModel):
    color: str
    title: str


class OldNote(Document):
    title: str
    tag: OldTag

    class Settings:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


class Forward:
    @iterative_migration()
    async def change_color(
        self, input_document: OldNote, output_document: Note
    ):
        output_document.tag.title = input_document.tag.name


class Backward:
    @iterative_migration()
    async def change_title(
        self, input_document: Note, output_document: OldNote
    ):
        output_document.tag.name = input_document.tag.title
