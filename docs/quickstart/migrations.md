## Create

To create new migration run:

```shell
beanie new-migration -n migration_name -p relative/path/to/migrations/directory/
```

It will create a file with name `*_migration_name.py` in the directory `relative/path/to/migrations/directory/`

Migration file contains two classes: `Forward` and `Backward`. Each one contains instructions to roll migration respectively forward and backward.

## Run

To roll one migration forward run:

```shell
beanie migrate -uri 'mongodb+srv://user:pass@host/db' -p relative/path/to/migrations/directory/ --distance 1
```

To roll all the migrations forward run:

```shell
beanie migrate -uri 'mongodb+srv://user:pass@host/db' -p relative/path/to/migrations/directory/
```

To roll one migration backward run:
```shell
beanie migrate -uri 'mongodb+srv://user:pass@host/db' -p relative/path/to/migrations/directory/ --distance 1 --backward
```

To roll all the migrations backward run:
```shell
beanie migrate -uri 'mongodb+srv://user:pass@host/db' -p relative/path/to/migrations/directory/ --backward
```

To show help message with all the parameters and descriptions run

```shell
beanie migrate --help
```

## Migration types

There are two types of instructions in the migration class:

- Iterative migration - instruction, which iterates throw all the documents of the input_document collection and update it
- Free fall migrations - instruction, where user can write any logic

### Iterative migrations

A simple example of field name changing. 

We have next models:

```python
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

```

To migrate from `OldNote` to `Note` I need to change filed `title` to field `name`.

Forward migration:

```python
class Forward:
    @iterative_migration()
    async def name_to_title(
        self, input_document: OldNote, output_document: Note
    ):
        output_document.title = input_document.name

```

Backward migration:

```python
class Backward:
    @iterative_migration()
    async def title_to_name(
        self, input_document: Note, output_document: OldNote
    ):
        output_document.name = input_document.title
```

And more complex example:

```python
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

    class Collection:
        name = "notes"


class Note(Document):
    title: str
    tag: Tag

    class Collection:
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
```

All the migrations examples can be found by [link](https://github.com/roman-right/beanie/tree/feature/migrations/tests/migrations/migrations_for_test)

### Free fall migrations

It is a much more flexible migration type, which allows to implementation of any migration logic. But at the same time, it is more verbose.

The same example but with free fall migration type:

```python
from pydantic.main import BaseModel

from beanie import Document, free_fall_migration


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

```

All the migrations examples can be found by [link](https://github.com/roman-right/beanie/tree/feature/migrations/tests/migrations/migrations_for_test)
