import importlib
from typing import List, Type, Union, TYPE_CHECKING

from pymongo import MongoClient
from pymongo.database import Database
from yarl import URL

from beanie.sync.odm.interfaces.detector import ModelType

if TYPE_CHECKING:
    from beanie.sync.odm.documents import DocType
    from beanie.sync.odm.views import View


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


def init_beanie(
    database: Database = None,
    connection_string: str = None,
    document_models: List[Union[Type["DocType"], Type["View"], str]] = None,
    allow_index_dropping: bool = False,
    recreate_views: bool = False,
):
    """
    Beanie initialization

    :param database: Database - pymongo database instance
    :param connection_string: str - MongoDB connection string
    :param document_models: List[Union[Type[DocType], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default False
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
        database = MongoClient(connection_string)[
            URL(connection_string).path[1:]
        ]

    sort_order = {
        ModelType.UnionDoc: 0,
        ModelType.Document: 1,
        ModelType.View: 2,
    }

    document_models_unwrapped: List[Union[Type[DocType], Type[View]]] = [
        get_model(model) if isinstance(model, str) else model
        for model in document_models
    ]

    document_models_unwrapped.sort(
        key=lambda val: sort_order[val.get_model_type()]
    )

    for model in document_models_unwrapped:
        if model.get_model_type() == ModelType.UnionDoc:
            model.init(database)

        if model.get_model_type() == ModelType.Document:
            model.init_model(
                database, allow_index_dropping=allow_index_dropping
            )
        if model.get_model_type() == ModelType.View:
            model.init_view(database, recreate_view=recreate_views)
