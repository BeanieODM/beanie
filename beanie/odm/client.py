import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Type

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing_extensions import Self

from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.odm.documents import Document
from beanie.odm.utils.init import init_beanie

logger = logging.getLogger(__name__)


class ODMClient:
    """
    An asynchronous ODM client for managing MongoDB connections using PyMongo and Beanie.
    """

    def __init__(self, uri: str, **kwargs: Any) -> None:
        """Initializes the ODM client."""
        self.uri = uri
        self.client: AsyncMongoClient = AsyncMongoClient(uri, **kwargs)
        self.databases: Dict[str, AsyncDatabase] = {}
        self._migration_lock = asyncio.Lock()

    async def init_db(
        self,
        db_config: Dict[str, List[Type[Document]]],
        migrations_path: Optional[str] = None,
    ):
        """
        Initializes all specified databases and their models from a configuration.

        Args:
            db_config (Dict[str, List[Type[Document]]]): A dictionary where keys are
                                                        database names and values are lists
                                                        of Beanie Document classes.
            migrations_path (Optional[str]): Path to the migrations directory.
        """
        tasks = [
            self.register_database(db_name, models, migrations_path)
            for db_name, models in db_config.items()
        ]
        await asyncio.gather(*tasks)

    async def register_database(
        self,
        db_name: str,
        models: List[Type[Document]],
        migrations_path: Optional[str] = None,
    ):
        """Initializes Beanie for a specific database with its document models."""
        if db_name in self.databases:
            logger.info(f"Database {db_name} is already registered.")
            return

        logger.info(f"Initializing database: {db_name}")
        db = self.client[db_name]

        # Handle Migrations
        if migrations_path and os.path.exists(migrations_path):
            logger.info(
                f"Running migrations for {db_name} from {migrations_path}"
            )
            settings = MigrationSettings(
                connection_uri=self.uri,
                database_name=db_name,
                path=migrations_path,
            )
            async with self._migration_lock:
                await run_migrate(settings)

        await init_beanie(
            database=db,
            document_models=models,
        )

        self.databases[db_name] = db
        logger.info(f"Successfully initialized database: {db_name}")

    def get_database(self, db_name: str) -> Optional[AsyncDatabase]:
        """Retrieves a registered database instance by its name."""
        return self.databases.get(db_name)

    async def close(self):
        """Closes the underlying MongoDB client connection."""
        if self.client:
            await self.client.close()
            logger.info("MongoDB client connection closed.")

    async def __aenter__(self) -> Self:
        """
        Async context manager entry point. Returns the client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point. Ensures the connection is closed.
        """
        await self.close()
