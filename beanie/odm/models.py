from typing import List

from pydantic import BaseModel

from beanie.exceptions import UniqueFieldExists
from beanie.odm.enums import InspectionStatuses
from beanie.odm.fields import PydanticObjectId
from beanie.odm.actions import (
    Insert,
    Replace,
    before_event,
)


class InspectionError(BaseModel):
    """
    Inspection error details
    """

    document_id: PydanticObjectId
    error: str


class InspectionResult(BaseModel):
    """
    Collection inspection result
    """

    status: InspectionStatuses = InspectionStatuses.OK
    errors: List[InspectionError] = []


class UniqueFieldsModel: # noqa
    @before_event([Insert, Replace])
    async def check_for_unique_fields(self):
        unique_fields = self.get_unique_fields()
        if unique_fields:
            for field in unique_fields:
                try:
                    if await self.find_one({field: getattr(self, field)}):
                        raise UniqueFieldExists
                    continue
                except AttributeError:
                    pass
