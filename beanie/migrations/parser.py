from typing import Type

import motor

from beanie import init_beanie
from beanie.migrations.controllers import Migration


def get_cli():
    return motor.motor_asyncio.AsyncIOMotorClient()


def get_db(client):
    return client.beanie_db


async def parse_migration_class(cls: Type):
    migrations = [
        getattr(cls, migration)
        for migration in dir(cls)
        if isinstance(getattr(cls, migration), Migration)
    ]

    client = get_cli()
    db = get_db(client)

    async with await client.start_session() as s:
        async with s.start_transaction():
            structures = []
            for migration in migrations:
                structures += migration.structures

            await init_beanie(database=db, document_models=structures)

            for migration in migrations:
                await migration.run(session=s)
