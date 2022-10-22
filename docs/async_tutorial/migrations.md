## Attention!

Migrations use transactions inside. It works only with **MongoDB replica sets**

## Create

To create a new migration run:

```shell
beanie new-migration -n migration_name -p relative/path/to/migrations/directory/
```

It will create a file with the name `*_migration_name.py` in the directory `relative/path/to/migrations/directory/`

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

Migration class contains instructions - decorated async functions. There are two types of instructions:

- Iterative migration - instruction, which iterates over all the documents of the input_document collection and updates it. Most comfortable to use. Can be used in 99% cases.
- Free fall migrations - instruction, where user can write any logic. Most flexible, but verbose.

### Iterative migrations

To mark a function as iterative migration must be used decorator `@iterative_migration()`. The function itself as parameters must have `input_document` with type and `output_document` with type. Like here:

```python
@iterative_migration()


async def name_to_title(
        self, input_document: OldNote, output_document: Note
):
```

#### A simple example of field name changing

There are the next models:

```python
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

```

To migrate from `OldNote` to `Note` filed `name` has to be renamed to `title`.

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

And a little more complex example:

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
```

All the migrations examples can be found by [link](https://github.com/roman-right/beanie/tree/main/tests/migrations/migrations_for_test)

### Free fall migrations

It is a much more flexible migration type, which allows to implementation of any migration logic. But at the same time, it is more verbose.

To mark function as a free fall migration, must be used decorator `@free_fall_migration()` with the list of Document classes, which will be used in this migration. Function itself receives `session` as a parameter. It is used to be able to roll back the migration, if something went wrong. To be able to roll back, please provide session into the Documents methods. Like here:

```python
@free_fall_migration(document_models=[OldNote, Note])
async def name_to_title(self, session):
    async for old_note in OldNote.find_all():
        new_note = Note(
            id=old_note.id, title=old_note.name, tag=old_note.tag
        )
        await new_note.replace(session=session)
```

#### The same example as for the iterative migration, but with free fall migration type

```python
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

```

All the migrations examples can be found by [link](https://github.com/roman-right/beanie/tree/main/tests/migrations/migrations_for_test)
