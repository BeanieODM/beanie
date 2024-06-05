import sys

from beanis.odm.documents import DocType, Document
from beanis.odm.fields import ExpressionField
from beanis.odm.settings.base import ItemSettings
from beanis.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_model_fields,
    parse_model,
)
from redis import Redis


if sys.version_info >= (3, 8):
    pass
else:
    pass

import importlib
import inspect
from typing import (  # type: ignore
    List,
    Optional,
    Type,
    Union,
)

from pydantic import BaseModel

from beanis.exceptions import Deprecation
from beanis.odm.actions import ActionRegistry

from beanis.odm.registry import DocsRegistry


class Output(BaseModel):
    class_name: str
    collection_name: str


class Initializer:
    def __init__(
        self,
        database: Redis = None,
        document_models: Optional[List[Union[Type["DocType"], str]]] = None,
    ):
        """
        Beanie initializer

        :param database: AsyncIOMotorDatabase - database instance
        :param document_models: List[Union[Type[DocType], str]] - model classes
        or strings with dot separated paths


        :return: None
        """

        self.inited_classes: List[Type] = []

        self.models_with_updated_forward_refs: List[Type[BaseModel]] = []

        if document_models is None:
            raise ValueError("document_models parameter must be set")

        self.database: Redis = database

        self.document_models: List[Union[Type[DocType]]] = [
            self.get_model(model) if isinstance(model, str) else model
            for model in document_models
        ]

        self.fill_docs_registry()

    def __await__(self):
        for model in self.document_models:
            yield from self.init_class(model).__await__()

    # General
    def fill_docs_registry(self):
        for model in self.document_models:
            module = inspect.getmodule(model)
            members = inspect.getmembers(module)
            for name, obj in members:
                if inspect.isclass(obj) and issubclass(obj, BaseModel):
                    DocsRegistry.register(name, obj)

    @staticmethod
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

    def init_settings(
        self, cls: Union[Type[Document]]
    ):
        """
        Init Settings

        :param cls: Union[Type[Document], Type[View], Type[UnionDoc]] - Class
        to init settings
        :return: None
        """
        settings_class = getattr(cls, "Settings", None)
        settings_vars = {} if settings_class is None else dict(vars(settings_class))
        if issubclass(cls, Document):
            cls._document_settings = parse_model(ItemSettings, settings_vars)

    if not IS_PYDANTIC_V2:

        def update_forward_refs(self, cls: Type[BaseModel]):
            """
            Update forward refs

            :param cls: Type[BaseModel] - class to update forward refs
            :return: None
            """
            if cls not in self.models_with_updated_forward_refs:
                cls.update_forward_refs()
                self.models_with_updated_forward_refs.append(cls)

    # General. Relations

    # Document

    @staticmethod
    def set_default_class_vars(cls: Type[Document]):
        """
        Set default class variables.

        :param cls: Union[Type[Document], Type[View], Type[UnionDoc]] - Class
        to init settings
        :return:
        """
        cls._children = dict()
        cls._parent = None
        cls._inheritance_inited = False
        cls._class_id = None
        cls._link_fields = None

    def init_document_fields(self, cls) -> None:
        """
        Init class fields
        :return: None
        """

        if not IS_PYDANTIC_V2:
            self.update_forward_refs(cls)

        if cls._link_fields is None:
            cls._link_fields = {}
        for k, v in get_model_fields(cls).items():
            path = v.alias or k
            setattr(cls, k, ExpressionField(path))

        cls.check_hidden_fields()

    @staticmethod
    def init_actions(cls):
        """
        Init event-based actions
        """
        ActionRegistry.clean_actions(cls)
        for attr in dir(cls):
            f = getattr(cls, attr)
            if inspect.isfunction(f):
                if hasattr(f, "has_action"):
                    ActionRegistry.add_action(
                        document_class=cls,
                        event_types=f.event_types,  # type: ignore
                        action_direction=f.action_direction,  # type: ignore
                        funct=f,
                    )

    def init_document_collection(self, cls):
        """
        Init collection for the Document-based class
        :param cls:
        :return:
        """
        cls.set_database(self.database)

        document_settings = cls.get_settings()

        if not document_settings.name:
            document_settings.name = cls.__name__

    async def init_document(self, cls: Type[Document]) -> Optional[Output]:
        """
        Init Document-based class

        :param cls:
        :return:
        """
        if cls is Document:
            return None

        # get db version
        if cls not in self.inited_classes:
            self.set_default_class_vars(cls)
            self.init_settings(cls)

            bases = [b for b in cls.__bases__ if issubclass(b, Document)]
            if len(bases) > 1:
                return None
            parent = bases[0]
            output = await self.init_document(parent)
            if cls.get_settings().is_root and (
                parent is Document or not parent.get_settings().is_root
            ):
                if cls.get_collection_name() is None:
                    cls.set_collection_name(cls.__name__)
                output = Output(
                    class_name=cls.__name__,
                    collection_name=cls.get_collection_name(),
                )
                cls._class_id = cls.__name__
                cls._inheritance_inited = True
            elif output is not None:
                output.class_name = f"{output.class_name}.{cls.__name__}"
                cls._class_id = output.class_name
                cls.set_collection_name(output.collection_name)
                parent.add_child(cls._class_id, cls)
                cls._parent = parent
                cls._inheritance_inited = True

            self.init_document_collection(cls)
            self.init_document_fields(cls)

            self.inited_classes.append(cls)

            return output

        else:
            if cls._inheritance_inited is True:
                return Output(
                    class_name=cls._class_id,
                    collection_name=cls.get_collection_name(),
                )
            else:
                return None

    # Deprecations

    @staticmethod
    async def check_deprecations(cls: Union[Type[Document]]):
        if hasattr(cls, "Collection"):
            raise Deprecation(
                "Collection inner class is not supported more. "
                "Please use Settings instead. "
                "https://beanie-odm.dev/tutorial/defining-a-document/#settings"
            )

    # Final

    async def init_class(self, cls: Union[Type[Document]]):
        """
        Init Document, View or UnionDoc based class.

        :param cls:
        :return:
        """
        await self.check_deprecations(cls)

        await self.init_document(cls)


async def init_beanis(
    database: Redis = None,
    document_models: Optional[
        List[Union[Type[Document], str]]
    ] = None,
    allow_index_dropping: bool = False,
    recreate_views: bool = False,
    multiprocessing_mode: bool = False,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param connection_string: str - MongoDB connection string
    :param document_models: List[Union[Type[DocType], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default False
    :param recreate_views: bool - if views should be recreated. Default False
    :param multiprocessing_mode: bool - if multiprocessing mode is on
        it will patch the motor client to use process's event loop. Default False
    :return: None
    """

    await Initializer(
        database=database,
        document_models=document_models
    )
