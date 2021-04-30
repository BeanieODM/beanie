import importlib.util
import logging
from pathlib import Path
from typing import Type, Optional

from beanie.odm.documents import Document
from beanie.odm.utils.general import init_beanie
from beanie.migrations.controllers.iterative import BaseMigrationController
from beanie.migrations.database import DBHandler
from beanie.migrations.models import (
    MigrationLog,
    RunningMode,
    RunningDirections,
)

logger = logging.getLogger(__name__)


class MigrationNode:
    def __init__(
        self,
        name: str,
        forward_class: Optional[Type[Document]] = None,
        backward_class: Optional[Type[Document]] = None,
        next_migration: Optional["MigrationNode"] = None,
        prev_migration: Optional["MigrationNode"] = None,
    ):
        """
        Node of the migration linked list

        :param name: name of the migration
        :param forward_class: Forward class of the migration
        :param backward_class: Backward class of the migration
        :param next_migration: link to the next migration
        :param prev_migration: link to the previous migration
        """
        self.name = name
        self.forward_class = forward_class
        self.backward_class = backward_class
        self.next_migration = next_migration
        self.prev_migration = prev_migration

    @staticmethod
    async def clean_current_migration():
        await MigrationLog.find(
            {"is_current": True},
        ).update({"$set": {"is_current": False}})

    async def update_current_migration(self):
        """
        Set sel as a current migration

        :return:
        """
        await self.clean_current_migration()
        await MigrationLog(is_current=True, name=self.name).insert()

    async def run(self, mode: RunningMode, allow_index_dropping: bool):
        """
        Migrate

        :param mode: RunningMode
        :param allow_index_dropping: if index dropping is allowed
        :return: None
        """
        if mode.direction == RunningDirections.FORWARD:
            migration_node = self.next_migration
            if migration_node is None:
                return None
            if mode.distance == 0:
                logger.info("Running migrations forward without limit")
                while True:
                    await migration_node.run_forward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
            else:
                logger.info(f"Running {mode.distance} migrations forward")
                for i in range(mode.distance):
                    await migration_node.run_forward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
        elif mode.direction == RunningDirections.BACKWARD:
            migration_node = self
            if mode.distance == 0:
                logger.info("Running migrations backward without limit")
                while True:
                    await migration_node.run_backward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break
            else:
                logger.info(f"Running {mode.distance} migrations backward")
                for i in range(mode.distance):
                    await migration_node.run_backward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break

    async def run_forward(self, allow_index_dropping):
        if self.forward_class is not None:
            await self.run_migration_class(
                self.forward_class, allow_index_dropping=allow_index_dropping
            )
        await self.update_current_migration()

    async def run_backward(self, allow_index_dropping):
        if self.backward_class is not None:
            await self.run_migration_class(
                self.backward_class, allow_index_dropping=allow_index_dropping
            )
        if self.prev_migration is not None:
            await self.prev_migration.update_current_migration()
        else:
            await self.clean_current_migration()

    async def run_migration_class(self, cls: Type, allow_index_dropping: bool):
        """
        Run Backward or Forward migration class

        :param cls:
        :param allow_index_dropping: if index dropping is allowed
        :return:
        """
        migrations = [
            getattr(cls, migration)
            for migration in dir(cls)
            if isinstance(getattr(cls, migration), BaseMigrationController)
        ]

        client = DBHandler().get_cli()
        db = DBHandler().get_db()

        async with await client.start_session() as s:
            async with s.start_transaction():
                for migration in migrations:
                    for model in migration.models:
                        await init_beanie(
                            database=db,
                            document_models=[model],  # TODO this is slow
                            allow_index_dropping=allow_index_dropping,
                        )
                    logger.info(
                        f"Running migration {migration.function.__name__} "
                        f"from module {self.name}"
                    )
                    await migration.run(session=s)

    @classmethod
    async def build(cls, path: Path):
        """
        Build the migrations linked list

        :param path: Relative path to the migrations directory
        :return:
        """
        logger.info("Building migration list")
        names = []
        for module in path.glob("*.py"):
            names.append(module.name)
        names.sort()

        db = DBHandler().get_db()
        await init_beanie(database=db, document_models=[MigrationLog])
        current_migration = await MigrationLog.find_one({"is_current": True})

        root_migration_node = MigrationNode("root")
        prev_migration_node = root_migration_node

        for name in names:
            spec = importlib.util.spec_from_file_location(
                (path / name).stem, (path / name).absolute()
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            forward_class = getattr(module, "Forward", None)
            backward_class = getattr(module, "Backward", None)
            migration_node = MigrationNode(
                name=name,
                prev_migration=prev_migration_node,
                forward_class=forward_class,
                backward_class=backward_class,
            )
            prev_migration_node.next_migration = migration_node
            prev_migration_node = migration_node

            if (
                current_migration is not None
                and current_migration.name == name
            ):
                root_migration_node = migration_node

        return root_migration_node
