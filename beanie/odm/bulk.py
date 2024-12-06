from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, Union

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

if TYPE_CHECKING:
    from beanie import Document


class BulkWriter:
    """
    A utility class for managing and executing bulk operations in MongoDB using Motor.

    This class facilitates efficient execution of multiple database operations,
    such as inserts, updates, deletes, and replacements, in a single batch.
    It supports asynchronous context management, ensuring that all queued
    operations are committed upon exiting the context.

    Attributes:
        session (Optional[AsyncIOMotorClientSession]): The MongoDB session used
            for transactional operations. Defaults to None.
        ordered (bool): If True (default), operations are executed sequentially,
            stopping on the first failure. If False, operations may execute in
            parallel, and all operations are attempted regardless of failures.
        operations (List[Union[DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne]]):
            A list of queued MongoDB operations to be executed in bulk.
        object_class (Optional[Type[Document]]): The document model class
            associated with the operations. All operations must belong to the
            same model class.

    Parameters:
        session (Optional[AsyncIOMotorClientSession]): The MongoDB session for
            transaction support. Defaults to None.
        ordered (bool): Specifies the execution order of bulk operations.
            Defaults to True.
    """

    def __init__(
        self,
        session: Optional[AsyncIOMotorClientSession] = None,
        ordered: bool = True,
    ):
        self.operations: List[
            Union[
                DeleteMany,
                DeleteOne,
                InsertOne,
                ReplaceOne,
                UpdateMany,
                UpdateOne,
            ]
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
        Commit all queued operations to the database.

        Executes all queued operations in a single bulk write request. If there
        are no operations to commit, it returns None.

        :return: The result of the bulk write operation if operations are committed.
                Returns None if there are no operations to execute.
        :rtype: Optional[BulkWriteResult]

        :raises ValueError: If the object_class is not specified before committing.
        """
        if not self.operations:
            return None
        if not self.object_class:
            raise ValueError(
                "The document model class must be specified before committing operations."
            )
        return await self.object_class.get_motor_collection().bulk_write(
            self.operations, session=self.session, ordered=self.ordered
        )

    def add_operation(
        self,
        object_class: Type[Document],
        operation: Union[
            DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne
        ],
    ):
        """
        Add an operation to the queue.

        This method adds a MongoDB operation to the BulkWriter's operation queue.
        All operations in the queue must belong to the same document model class.

        :param object_class: The document model class associated with the operation.
        :type object_class: Type[Document]
        :param operation: The MongoDB operation to add to the queue.
        :type operation: Union[DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne]

        :raises ValueError: If the operation's document model class differs from
                            the one already associated with the BulkWriter.
        """
        if self.object_class is None:
            self.object_class = object_class
        else:
            if object_class != self.object_class:
                raise ValueError(
                    "All the operations should be for a single document model"
                )
        self.operations.append(operation)
