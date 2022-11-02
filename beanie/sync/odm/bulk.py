from typing import Dict, Any, List, Optional, Union, Type, Mapping

from pydantic import BaseModel
from pymongo import (
    InsertOne,
    DeleteOne,
    DeleteMany,
    ReplaceOne,
    UpdateOne,
    UpdateMany,
)


class Operation(BaseModel):
    operation: Union[
        Type[InsertOne],
        Type[DeleteOne],
        Type[DeleteMany],
        Type[ReplaceOne],
        Type[UpdateOne],
        Type[UpdateMany],
    ]
    first_query: Mapping[str, Any]
    second_query: Optional[Dict[str, Any]] = None
    object_class: Type

    class Config:
        arbitrary_types_allowed = True


class BulkWriter:
    def __init__(self):
        self.operations: List[Operation] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.commit()

    def commit(self):
        obj_class = None
        requests = []
        if self.operations:
            for op in self.operations:
                if obj_class is None:
                    obj_class = op.object_class

                if obj_class != op.object_class:
                    raise ValueError(
                        "All the operations should be for a single document model"
                    )
                if op.operation in [InsertOne, DeleteOne]:
                    query = op.operation(op.first_query)
                else:
                    query = op.operation(op.first_query, op.second_query)
                requests.append(query)

            obj_class.get_motor_collection().bulk_write(requests)  # type: ignore

    def add_operation(self, operation: Operation):
        self.operations.append(operation)
