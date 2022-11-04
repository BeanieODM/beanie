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


class Backward:
    @iterative_migration()
    async def change_title(self, input_document: Note, output_document: Note):
        if input_document.title == "three":
            output_document.title = "3"
