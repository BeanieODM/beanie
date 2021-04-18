import asyncio
import importlib
from typing import List, Type, Union

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie.odm.documents import Document


def get_model(dot_path: str) -> Type[Document]:
    """
    Get the model by the path in format bar.foo.Model

    :param dot_path: str - dot seprated path to the model
    :return: Type[Document] - class of the model
    """
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
    database: AsyncIOMotorDatabase,
    document_models: List[Union[Type[Document], str]],
    allow_index_dropping: bool = True,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param document_models: List[Union[Type[Document], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default True
    :return: None
    """
    collection_inits = []
    for model in document_models:
        if isinstance(model, str):
            model = get_model(model)
        collection_inits.append(
            model.init_collection(
                database, allow_index_dropping=allow_index_dropping
            )
        )

    await asyncio.gather(*collection_inits)
