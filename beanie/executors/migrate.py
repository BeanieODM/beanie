import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import click
import toml
from pydantic import BaseSettings

from beanie.migrations import template
from beanie.migrations.database import DDHandler
from beanie.migrations.models import RunningMode, RunningDirections
from beanie.migrations.runner import MigrationNode


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
    uri: str
    db: str
    path: Path

    class Config:
        env_prefix = "beanie_"
        fields = {
            "uri": {
                "env": [
                    "uri",
                    "connection_string",
                    "mongodb_dsn",
                    "mongodb_url",
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
    DDHandler().set_db(settings.uri, settings.db)
    root = await MigrationNode.build(settings.path)
    mode = RunningMode(
        direction=settings.direction, distance=settings.distance
    )
    await root.run(mode=mode)


@migrations.command()
@click.option(
    "--forward",
    "direction",
    required=False,
    flag_value="FORWARD",
    help="Direction of the migration",
)
@click.option(
    "--backward",
    "direction",
    required=False,
    flag_value="BACKWARD",
    help="Direction of the migration",
)
@click.option(
    "-d",
    "--distance",
    required=False,
    help="How many migrations should be done",
)
@click.option("--uri", required=False, type=str, help="MongoDB connection URI")
@click.option("--db", required=False, type=str, help="DataBase name")
@click.option(
    "-p",
    "--path",
    required=False,
    type=str,
    help="Path to the migrations directory",
)
def migrate(direction, distance, uri, db, path):
    settings_kwargs = {}
    if direction:
        settings_kwargs["direction"] = direction
    if distance:
        settings_kwargs["distance"] = distance
    if uri:
        settings_kwargs["uri"] = uri
    if db:
        settings_kwargs["db"] = db
    if path:
        settings_kwargs["path"] = path
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
