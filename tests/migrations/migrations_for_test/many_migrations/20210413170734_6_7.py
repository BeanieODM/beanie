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
    async def change_title_6(
        self, input_document: Note, output_document: Note
    ):
        if input_document.title == "6":
            output_document.title = "six"

    @iterative_migration()
    async def change_title_7(
        self, input_document: Note, output_document: Note
    ):
        if input_document.title == "7":
            output_document.title = "seven"


class Backward:
    @iterative_migration()
    async def change_title_7(
        self, input_document: Note, output_document: Note
    ):
        if input_document.title == "seven":
            output_document.title = "7"

    @iterative_migration()
    async def change_title_6(
        self, input_document: Note, output_document: Note
    ):
        if input_document.title == "six":
            output_document.title = "6"
