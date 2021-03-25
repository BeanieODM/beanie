import asyncio
import importlib
from typing import List, Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie import Document


def get_model(dot_path: str) -> Type[Document]:
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
    database: AsyncIOMotorDatabase, document_models: List[Type[Document]]
):
    collection_inits = []
    for model in document_models:
        if isinstance(model, str):
            model = get_model(model)
        collection_inits.append(model.init_collection(database))

    await asyncio.gather(*collection_inits)
