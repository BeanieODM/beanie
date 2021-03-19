import importlib

from typing import List, Type, Union

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie import Document


def get_model(dot_path: str) -> Type[Document]:
    try:
        module_name, class_name = dot_path.rsplit(".", 1)
        return getattr(importlib.import_module(module_name), class_name)

    except ValueError:
        raise ValueError(f"'{dot_path}' doesn't have '.' path, eg. path.to.your.model.class")

    except AttributeError:
        raise AttributeError(f"module '{module_name}' has no class called '{class_name}'")


def init_beanie(database: AsyncIOMotorDatabase, document_models: List[Union[Type[Document], str]]):
    for model_path in document_models:
        model = get_model(model_path) if isinstance(model_path, str) else model_path
        model._create_collection(database)
