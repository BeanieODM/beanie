from typing import List, Optional, Type, Union

from beanie import Document
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import (
    DeleteMany,
    DeleteOne,
    InsertOne,
    ReplaceOne,
    UpdateMany,
    UpdateOne,
)
from pymongo.results import BulkWriteResult

"""
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import ConfigDict

    if IS_PYDANTIC_V2:
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
    else:

        class Config:
            arbitrary_types_allowed = True
"""


class BulkWriter:
    def __init__(
        self,
        session: Optional[AsyncIOMotorClientSession] = None,
        ordered: bool = True,
    ):
        self.operations: List[
            Union[DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne]
        ] = []
        self.session = session
        self.ordered = ordered
        self.object_class: Optional[Type[Document]] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.commit()

    async def commit(self) -> Optional[BulkWriteResult]:
        """
        Commit all the operations to the database
        :return:
        """
        if self.operations:
            assert self.object_class
            return await self.object_class.get_motor_collection().bulk_write(
                self.operations, session=self.session, ordered=self.ordered
            )
        return None

    def add_operation(
        self,
        object_class: Type[Document],
        operation: Union[
            DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne
        ],
    ):
        if self.object_class is None:
            self.object_class = object_class
        else:
            if object_class != self.object_class:
                raise ValueError(
                    "All the operations should be for a single document model"
                )
        self.operations.append(operation)
