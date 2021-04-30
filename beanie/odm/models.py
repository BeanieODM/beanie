from typing import List, Optional, Union, Tuple

import pymongo
from pydantic import BaseModel, validator

from beanie.odm.enums import SortDirection, InspectionStatuses
from beanie.odm.fields import PydanticObjectId


class FindOperationKWARGS(BaseModel):
    """
    KWARGS Parser for find operators
    """

    skip: Optional[int] = None
    limit: Optional[int] = None
    sort: Union[None, str, List[Tuple[str, SortDirection]]] = None

    @validator("sort")
    def str_to_sorting_tuple(cls, v):
        if isinstance(v, str):
            return [(v, pymongo.ASCENDING)]
        return v


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
