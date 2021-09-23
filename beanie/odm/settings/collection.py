from typing import List, Type

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic.main import BaseModel
from pymongo import IndexModel


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
    use_state_management: bool = False
    indexes: List[IndexModelField] = []

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

        # create motor collection
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
        if allow_index_dropping:
            for index in set(old_indexes) - set(new_indexes):
                await collection.drop_index(index)

        return cls(
            name=collection_parameters.name,
            motor_collection=collection,
        )
