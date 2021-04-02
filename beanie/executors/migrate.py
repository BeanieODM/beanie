import asyncio
import shutil
from datetime import datetime
from pathlib import Path

import click
from pydantic import BaseSettings

from beanie.migrations import template
from beanie.migrations.database import DDHandler
from beanie.migrations.models import RunningMode, RunningDirections
from beanie.migrations.runner import MigrationNode


class MigrationSettings(BaseSettings):
    direction: RunningDirections = RunningDirections.FORWARD
    distance: int = 0
    uri: str
    db: str
    path: Path


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
    default=True,
    flag_value="FORWARD",
    help="Direction of the migration",
    show_default=True,
)
@click.option(
    "--backward",
    "direction",
    flag_value="BACKWARD",
    help="Direction of the migration",
)
@click.option(
    "-d",
    "--distance",
    default=0,
    help="How many migrations should be done",
    show_default=True,
)
@click.option("--uri", required=True, type=str, help="MongoDB connection URI")
@click.option("--db", required=True, type=str, help="DataBase name")
@click.option(
    "-p",
    "--path",
    required=True,
    type=str,
    help="Path to the migrations directory",
)
def migrate(direction, distance, uri, db, path):
    settings = MigrationSettings(
        direction=direction, distance=distance, uri=uri, db=db, path=path
    )
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
