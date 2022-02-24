from typing import List, Type, Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic.main import BaseModel
from pymongo import IndexModel

from beanie.exceptions import MongoDBVersionError
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


class CollectionInputParameters(BaseModel):
    name: str = ""
    indexes: List[IndexModelField] = []
    timeseries: Optional[TimeSeriesConfig]

    class Config:
        arbitrary_types_allowed = True


class CollectionSettings(BaseModel):
    name: str
    motor_collection: AsyncIOMotorCollection

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def init(
        cls,
        database: AsyncIOMotorDatabase,
        document_model: Type,
        allow_index_dropping: bool,
    ) -> "CollectionSettings":
        """
        Collection settings factory.
        Creates private property _collection_settings
        for the Document on the init step,

        :param database: AsyncIOMotorDatabase - Motor database instance
        :param document_model: Type - a class, inherited from Document class
        :param allow_index_dropping: bool - if index dropping is allowed
        :return: CollectionSettings
        """
        # parse collection parameters
        collection_class = getattr(document_model, "Collection", None)
        if collection_class:
            collection_parameters = CollectionInputParameters.parse_obj(
                vars(collection_class)
            )
        else:
            collection_parameters = CollectionInputParameters()

        # set collection name
        if not collection_parameters.name:
            collection_parameters.name = document_model.__name__

        # check mongodb version
        build_info = await database.command({"buildInfo": 1})
        mongo_version = build_info["version"]
        major_version = int(mongo_version.split(".")[0])

        if collection_parameters.timeseries is not None and major_version < 5:
            raise MongoDBVersionError(
                "Timeseries are supported by MongoDB version 5 and higher"
            )

        # create motor collection
        if (
            collection_parameters.timeseries is not None
            and collection_parameters.name
            not in await database.list_collection_names()
        ):

            collection = await database.create_collection(
                **collection_parameters.timeseries.build_query(
                    collection_parameters.name
                )
            )
        else:
            collection = database[collection_parameters.name]

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
        if collection_parameters.indexes:
            found_indexes += collection_parameters.indexes

        # create indices
        if found_indexes:
            new_indexes += await collection.create_indexes(found_indexes)

        # delete indexes
        # Only drop indexes if the user specifically allows for it
        if allow_index_dropping:
            for index in set(old_indexes) - set(new_indexes):
                await collection.drop_index(index)

        return cls(
            name=collection_parameters.name,
            motor_collection=collection,
        )
