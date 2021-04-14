import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import click
import toml
from pydantic import BaseSettings

from beanie.migrations import template
from beanie.migrations.database import DBHandler
from beanie.migrations.models import RunningMode, RunningDirections
from beanie.migrations.runner import MigrationNode

logging.basicConfig(format="%(message)s", level=logging.INFO)


def toml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    path = Path("pyproject.toml")
    if path.is_file():
        return (
            toml.load(path)
            .get("tool", {})
            .get("beanie", {})
            .get("migrations", {})
        )
    return {}


class MigrationSettings(BaseSettings):
    direction: RunningDirections = RunningDirections.FORWARD
    distance: int = 0
    connection_uri: str
    database_name: str
    path: Path
    allow_index_dropping: bool = True

    class Config:
        env_prefix = "beanie_"
        fields = {
            "connection_uri": {
                "env": [
                    "uri",
                    "connection_uri",
                    "connection_string",
                    "mongodb_dsn",
                    "mongodb_uri",
                ]
            },
            "db": {"env": ["db", "db_name", "database_name"]},
        }

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                toml_config_settings_source,
                env_settings,
                file_secret_settings,
            )


@click.group()
def migrations():
    pass


async def run_migrate(settings: MigrationSettings):
    DBHandler().set_db(settings.connection_uri, settings.database_name)
    root = await MigrationNode.build(settings.path)
    mode = RunningMode(
        direction=settings.direction, distance=settings.distance
    )
    await root.run(
        mode=mode, allow_index_dropping=settings.allow_index_dropping
    )


@migrations.command()
@click.option(
    "--forward",
    "direction",
    required=False,
    flag_value="FORWARD",
    help="Roll the migrations forward. This is default",
)
@click.option(
    "--backward",
    "direction",
    required=False,
    flag_value="BACKWARD",
    help="Roll the migrations backward",
)
@click.option(
    "-d",
    "--distance",
    required=False,
    help="How many migrations should be done since the current? "
    "0 - all the migrations. Default is 0",
)
@click.option(
    "-uri",
    "--connection-uri",
    required=False,
    type=str,
    help="MongoDB connection URI",
)
@click.option(
    "-db", "--database_name", required=False, type=str, help="DataBase name"
)
@click.option(
    "-p",
    "--path",
    required=False,
    type=str,
    help="Path to the migrations directory",
)
@click.option(
    "--allow-index-dropping/--forbid-index-dropping",
    required=False,
    default=True,
)
def migrate(
    direction,
    distance,
    connection_uri,
    database_name,
    path,
    allow_index_dropping,
):
    settings_kwargs = {}
    if direction:
        settings_kwargs["direction"] = direction
    if distance:
        settings_kwargs["distance"] = distance
    if connection_uri:
        settings_kwargs["connection_uri"] = connection_uri
    if database_name:
        settings_kwargs["database_name"] = database_name
    if path:
        settings_kwargs["path"] = path
    if allow_index_dropping:
        settings_kwargs["allow_index_dropping"] = allow_index_dropping
    settings = MigrationSettings(**settings_kwargs)

    asyncio.run(run_migrate(settings))


@migrations.command()
@click.option("-n", "--name", required=True, type=str, help="Migration name")
@click.option(
    "-p",
    "--path",
    required=True,
    type=str,
    help="Path to the migrations directory",
)
def new_migration(name, path):
    path = Path(path)
    ts_string = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{ts_string}_{name}.py"

    shutil.copy(template.__file__, path / file_name)


if __name__ == "__main__":
    migrations()
