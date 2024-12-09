from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type, Union

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
    A utility class for managing and executing bulk operations.

    This class facilitates the efficient execution of multiple database operations
    (e.g., inserts, updates, deletes, replacements) in a single batch. It supports asynchronous
    context management and ensure that all queued operations are committed upon exiting the context.

    Attributes:
        session (Optional[AsyncIOMotorClientSession]): The motor session used for transactional operations.
            Defaults to None, meaning no session is used.
        ordered (bool): Specifies whether operations are executed sequentially (default) or in parallel.
            - If True, operations are performed serially, stopping at the first failure.
            - If False, operations may be executed in arbitrary order, and all operations are attempted
              regardless of individual failures.
        bypass_document_validation (bool): If True, document-level validation is bypassed for all operations
            in the bulk write. This applies to MongoDB's schema validation rules, allowing documents that
            do not meet validation criteria to be inserted or modified. Defaults to False.
        comment (Optional[Any]): A user-provided comment attached to the bulk operation command, useful for
            auditing and debugging purposes.
        operations (List[Union[DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne]]):
            A list of MongoDB operations queued for bulk execution.

    Parameters:
        session (Optional[AsyncIOMotorClientSession]): The motot session for transaction support.
            Defaults to None (no session).
        ordered (bool): Specifies whether operations are executed in sequence (True) or in parallel (False).
            Defaults to True.
        bypass_document_validation (bool): Allows the bulk operation to bypass document-level validation.
            This is particularly useful when working with schemas that are being phased in or for bulk imports
            where strict validation may not be necessary. Defaults to False.
        comment (Optional[Any]): A custom comment attached to the bulk operation.
    """

    def __init__(
        self,
        session: Optional[AsyncIOMotorClientSession] = None,
        ordered: bool = True,
        bypass_document_validation: bool = False,
        comment: Optional[Any] = None,
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
        self.bypass_document_validation = bypass_document_validation
        self.comment = comment
        self._colection_name: str

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
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
            self.operations,
            ordered=self.ordered,
            bypass_document_validation=self.bypass_document_validation,
            session=self.session,
            comment=self.comment,
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
        All operations in the queue must belong to the same collection.

        :param object_class: The document model class associated with the operation.
        :type object_class: Type[Document]
        :param operation: The MongoDB operation to add to the queue.
        :type operation: Union[DeleteMany, DeleteOne, InsertOne, ReplaceOne, UpdateMany, UpdateOne]

        :raises ValueError: If the collection differs from
                            the one already associated with the BulkWriter.
        """
        if self.object_class is None:
            self.object_class = object_class
            self._colection_name = object_class.get_collection_name()
        else:
            if object_class.get_collection_name() != self._colection_name:
                raise ValueError(
                    "All the operations should be for a same collection name"
                )
        self.operations.append(operation)
