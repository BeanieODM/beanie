from typing import List, Optional, Set

import motor.motor_asyncio
import pymongo.monitoring
import pytest
from pymongo.monitoring import CommandListener

from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic_settings import BaseSettings
else:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/beanie_db"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


# Command monitor to track MongoDB operations
class CommandLogger(CommandListener):
    def __init__(self, command_names_to_track: Optional[Set[str]] = None):
        self.commands: List[tuple] = []
        self.command_names_to_track: Set[str] = command_names_to_track or {
            "findAndModify",
        }

    def started(self, event):
        if event.command_name in self.command_names_to_track:
            self.commands.append((event.command_name, event.command))

    def succeeded(self, event):
        pass

    def failed(self, event):
        pass

    def clear(self):
        self.commands = []

    def get_commands_by_name(self, command_name: str):
        return [
            command for command in self.commands if command[0] == command_name
        ]


@pytest.fixture
def command_logger():
    """
    Fixture that provides a pre-configured CommandLogger for tracking MongoDB commands.
    The logger tracks "findAndModify", "update", "insert" commands.

    Returns:
        A configured CommandLogger instance
    """
    logger = CommandLogger({"findAndModify", "update", "insert"})
    pymongo.monitoring.register(logger)
    yield logger


@pytest.fixture()
def cli(settings, command_logger):
    return motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings):
    return cli[settings.mongodb_db_name]
