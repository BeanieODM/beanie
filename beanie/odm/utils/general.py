import asyncio
import importlib
from typing import List, Type, Union, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from yarl import URL

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


def get_model(dot_path: str) -> Type["DocType"]:
    """
    Get the model by the path in format bar.foo.Model

    :param dot_path: str - dot seprated path to the model
    :return: Type[DocType] - class of the model
    """
    module_name, class_name = None, None
    try:
        module_name, class_name = dot_path.rsplit(".", 1)
        return getattr(importlib.import_module(module_name), class_name)

    except ValueError:
        raise ValueError(
            f"'{dot_path}' doesn't have '.' path, eg. path.to.your.model.class"
        )

    except AttributeError:
        raise AttributeError(
            f"module '{module_name}' has no class called '{class_name}'"
        )


async def init_beanie(
    database: AsyncIOMotorDatabase = None,
    connection_string: str = None,
    document_models: List[Union[Type["DocType"], str]] = None,
    allow_index_dropping: bool = True,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param connection_string: str - MongoDB connection string
    :param document_models: List[Union[Type[DocType], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default True
    :return: None
    """
    if (connection_string is None and database is None) or (
        connection_string is not None and database is not None
    ):
        raise ValueError(
            "connection_string parameter or database parameter must be set"
        )

    if document_models is None:
        raise ValueError("document_models parameter must be set")
    if connection_string is not None:
        database = AsyncIOMotorClient(connection_string)[
            URL(connection_string).path[1:]
        ]

    collection_inits = []
    for model in document_models:
        if isinstance(model, str):
            model = get_model(model)
        collection_inits.append(
            model.init_model(
                database, allow_index_dropping=allow_index_dropping
            )
        )

    await asyncio.gather(*collection_inits)
