from pydantic.main import BaseModel

from beanie import Document, iterative_migration


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    title: str
    tag_name: str
    tag_color: str

    class Settings:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


class Forward:
    @iterative_migration()
    async def pack(self, input_document: OldNote, output_document: Note):
        output_document.tag = Tag(
            name=input_document.tag_name, color=input_document.tag_color
        )


class Backward:
    @iterative_migration()
    async def unpack(self, input_document: Note, output_document: OldNote):
        output_document.tag_name = input_document.tag.name
        output_document.tag_color = input_document.tag.color
