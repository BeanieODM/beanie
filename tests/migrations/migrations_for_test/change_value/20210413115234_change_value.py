from pydantic.main import BaseModel

from beanie import Document, iterative_migration


class Tag(BaseModel):
    color: str
    name: str


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


class Forward:
    @iterative_migration()
    async def change_title(self, input_document: Note, output_document: Note):
        if input_document.title == "5":
            output_document.title = "five"


class Backward:
    @iterative_migration()
    async def change_title(self, input_document: Note, output_document: Note):
        if input_document.title == "five":
            output_document.title = "5"
