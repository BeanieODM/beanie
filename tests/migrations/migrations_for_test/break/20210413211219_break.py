from pydantic.main import BaseModel

from beanie import Document, iterative_migration, PydanticObjectId, Indexed


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


fixed_id = PydanticObjectId("6076f1f3e4b7f6b7a0f6e5a0")


class Forward:
    @iterative_migration(batch_size=2)
    async def name_to_title(
        self, input_document: OldNote, output_document: Note
    ):
        output_document.title = input_document.name
        if output_document.title > "5":
            output_document.name = "5"


class Backward:
    @iterative_migration()
    async def title_to_name(
        self, input_document: Note, output_document: OldNote
    ):
        output_document.name = input_document.title
