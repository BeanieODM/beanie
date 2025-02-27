from typing import Callable, List, Optional, Set

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


@pytest.fixture()
def cli(settings):
    return motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings):
    return cli[settings.mongodb_db_name]


# Command monitor to track MongoDB operations
class CommandLogger(CommandListener):
    def __init__(self, command_names_to_track: Optional[Set[str]] = None):
        self.commands: List[tuple] = []
        self.command_names_to_track: Set[str] = command_names_to_track or {
            "update",
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


@pytest.fixture
def create_command_logger() -> Callable[[Optional[Set[str]]], CommandLogger]:
    """
    Fixture factory that provides a CommandLogger configured to track specific MongoDB commands.

    Example usage:
        def test_something(create_command_logger):
            logger = create_command_logger({"insert", "findAndModify"})
            # Use logger in test

    Args:
        command_names_to_track: Optional[Set[str]] - The names of commands to track (default: {"update", "findAndModify"})

    Returns:
        A factory function that returns a configured CommandLogger
    """
    loggers: List[CommandLogger] = []

    def _make_logger(
        command_names_to_track: Optional[Set[str]] = None,
    ) -> CommandLogger:
        logger = CommandLogger(command_names_to_track)
        pymongo.monitoring.register(logger)
        loggers.append(logger)
        return logger

    yield _make_logger

    # Clean up all created loggers
    for logger in loggers:
        pymongo.monitoring.unregister(logger)
