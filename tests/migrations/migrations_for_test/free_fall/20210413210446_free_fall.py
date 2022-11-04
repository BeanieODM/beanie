from pydantic.main import BaseModel

from beanie import Document, free_fall_migration


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    name: str
    tag: Tag

    class Settings:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


class Forward:
    @free_fall_migration(document_models=[OldNote, Note])
    async def name_to_title(self, session):
        async for old_note in OldNote.find_all():
            new_note = Note(
                id=old_note.id, title=old_note.name, tag=old_note.tag
            )
            await new_note.replace(session=session)


class Backward:
    @free_fall_migration(document_models=[OldNote, Note])
    async def title_to_name(self, session):
        async for old_note in Note.find_all():
            new_note = OldNote(
                id=old_note.id, name=old_note.title, tag=old_note.tag
            )
            await new_note.replace(session=session)
