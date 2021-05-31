import asyncio
import importlib
from typing import List, Type, Union, Dict, Any, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


def parse_model(model: Type[BaseModel], value: Dict[str, Any]) -> BaseModel:
    """
    Create a model object from dictionary. If model is subclass of
    the Document class, it will set _is_inserted property to True

    :param model: Type[BaseModel] - model to parse
    :param value: Dict[str, Any] - data
    :return: BaseModel
    """
    result = model.parse_obj(value)
    if hasattr(result, "_is_inserted"):
        result._is_inserted = True
    return result


def get_model(dot_path: str) -> Type["DocType"]:
    """
    Get the model by the path in format bar.foo.Model

    :param dot_path: str - dot seprated path to the model
    :return: Type[DocType] - class of the model
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
    document_models: List[Union[Type["DocType"], str]],
    allow_index_dropping: bool = True,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param document_models: List[Union[Type[DocType], str]] - model classes
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
