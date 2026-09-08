from typing import Any

from bson import ObjectId
from pydantic import BaseModel, field_serializer

from beanie.odm.enums import InspectionStatuses


class InspectionError(BaseModel):
    """
    Inspection error details

    The document ID is kept as stored, even when it does not match the
    document model's ID type.
    """

    document_id: Any
    error: str

    @field_serializer("document_id", when_used="json")
    def serialize_document_id(self, value: Any) -> Any:
        return str(value) if isinstance(value, ObjectId) else value


class InspectionResult(BaseModel):
    """
    Collection inspection result
    """

    status: InspectionStatuses = InspectionStatuses.OK
    errors: list[InspectionError] = []
