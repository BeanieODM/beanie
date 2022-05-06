import warnings
from typing import Optional, Type, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import Field
from pymongo import IndexModel

from beanie.exceptions import MongoDBVersionError
from beanie.odm.settings.base import ItemSettings
from beanie.odm.settings.timeseries import TimeSeriesConfig


class IndexModelField(IndexModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, IndexModel):
            return v
        else:
            return IndexModel(v)


class DocumentSettings(ItemSettings):
    use_state_management: bool = False
    state_management_replace_objects: bool = False
    validate_on_save: bool = False
    use_revision: bool = False

    indexes: List[IndexModelField] = Field(default_factory=list)
    timeseries: Optional[TimeSeriesConfig] = None

    @classmethod
    async def init(
        cls,
        database: AsyncIOMotorDatabase,
        document_model: Type,
        allow_index_dropping: bool,
    ) -> "DocumentSettings":

        settings_class = getattr(document_model, "Settings", None)
        settings_vars = (
            {} if settings_class is None else dict(vars(settings_class))
        )

        # deprecated Collection class support

        collection_class = getattr(document_model, "Collection", None)

        if collection_class is not None:
            warnings.warn(
                "Collection inner class is deprecated, use Settings instead",
                DeprecationWarning,
            )

        collection_vars = (
            {} if collection_class is None else dict(vars(collection_class))
        )

        settings_vars.update(collection_vars)

        # ------------------------------------ #

        document_settings = DocumentSettings.parse_obj(settings_vars)

        document_settings.motor_db = database

        # register in the Union Doc

        if document_settings.union_doc is not None:
            document_settings.name = document_settings.union_doc.register_doc(
                document_model
            )

        # set a name

        if not document_settings.name:
            document_settings.name = document_model.__name__

        # check mongodb version
        build_info = await database.command({"buildInfo": 1})
        mongo_version = build_info["version"]
        major_version = int(mongo_version.split(".")[0])

        if document_settings.timeseries is not None and major_version < 5:
            raise MongoDBVersionError(
                "Timeseries are supported by MongoDB version 5 and higher"
            )

        # create motor collection
        if (
            document_settings.timeseries is not None
            and document_settings.name
            not in await database.list_collection_names()
        ):

            collection = await database.create_collection(
                **document_settings.timeseries.build_query(
                    document_settings.name
                )
            )
        else:
            collection = database[document_settings.name]

        document_settings.motor_collection = collection

        # indexes
        old_indexes = (await collection.index_information()).keys()
        new_indexes = ["_id_"]

        # Indexed field wrapped with Indexed()
        found_indexes = [
            IndexModel(
                [
                    (
                        fvalue.alias,
                        fvalue.type_._indexed[0],
                    )
                ],
                **fvalue.type_._indexed[1]
            )
            for _, fvalue in document_model.__fields__.items()
            if hasattr(fvalue.type_, "_indexed") and fvalue.type_._indexed
        ]

        # get indexes from the Collection class
        if document_settings.indexes:
            found_indexes += document_settings.indexes

        # create indices
        if found_indexes:
            new_indexes += await collection.create_indexes(found_indexes)

        # delete indexes
        # Only drop indexes if the user specifically allows for it
        if allow_index_dropping:
            for index in set(old_indexes) - set(new_indexes):
                await collection.drop_index(index)

        return document_settings

    class Config:
        arbitrary_types_allowed = True
