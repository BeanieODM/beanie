import importlib
import pkgutil
from typing import Type, Optional

import motor

from beanie import init_beanie
from beanie.migrations.controllers import BaseMigrationController
from beanie.migrations.models import Migration, RunningMode, RunningDirections


def get_cli():
    return motor.motor_asyncio.AsyncIOMotorClient(
        serverSelectionTimeoutMS=1000
    )


def get_db(client):
    return client.beanie_db


class MigrationNode:
    def __init__(
        self,
        name,
        forward_class=None,
        backward_class=None,
        next_migration=None,
        prev_migration=None,
    ):
        self.name: str = name
        self.forward_class = forward_class
        self.backward_class = backward_class
        self.next_migration: Optional["MigrationNode"] = next_migration
        self.prev_migration: Optional["MigrationNode"] = prev_migration

    async def update_current_migration(self):  # TODO more options
        await Migration.delete_all()
        await Migration(is_current=True, name=self.name).create()

    async def run(self, mode: RunningMode):
        migration_node = self
        if mode.direction == RunningDirections.FORWARD:
            if mode.distance == 0:
                while True:
                    await migration_node.run_forward()
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
            else:
                for i in range(mode.distance):
                    await migration_node.run_forward()
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
        elif mode.direction == RunningDirections.BACKWARD:
            if mode.distance == 0:
                while True:
                    await migration_node.run_backward()
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break
            else:
                for i in range(mode.distance):
                    await migration_node.run_backward()
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break

    async def run_forward(self):
        if self.forward_class is not None:
            await self.run_migration_class(self.forward_class)
        await self.update_current_migration()

    async def run_backward(self):
        if self.backward_class is not None:
            await self.run_migration_class(self.backward_class)
        await self.update_current_migration()

    @staticmethod
    async def run_migration_class(cls: Type):
        migrations = [
            getattr(cls, migration)
            for migration in dir(cls)
            if isinstance(getattr(cls, migration), BaseMigrationController)
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

    @classmethod
    async def build(cls, path):
        names = []
        package = importlib.import_module(path)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            names.append(name)
        names.sort()

        client = get_cli()
        db = get_db(client)
        await init_beanie(database=db, document_models=[Migration])
        current_migration = await Migration.find_one({"is_current": True})

        root_migration_node = MigrationNode("root")
        prev_migration_node = root_migration_node
        for name in names:
            module = importlib.import_module(
                f"{path}.{name}"
            )  # TODO make it better way
            forward_class = getattr(module, "Forward", None)
            print(package, forward_class)
            backward_class = getattr(package, "Backward", None)
            migration_node = MigrationNode(
                name=name,
                prev_migration=prev_migration_node,
                forward_class=forward_class,
                backward_class=backward_class,
            )
            prev_migration_node.next_migration = migration_node
            if (
                current_migration is not None
                and current_migration.name == name
            ):
                root_migration_node = migration_node

        return root_migration_node
