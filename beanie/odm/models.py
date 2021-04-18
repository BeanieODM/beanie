from enum import Enum
from typing import List, Optional, Union, Tuple

import pymongo
from pydantic import BaseModel, validator

from beanie.odm.fields import PydanticObjectId


class SortDirection(int, Enum):
    """
    Sorting directions
    """

    ASCENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING


class FindOperationKWARGS(BaseModel):
    """
    KWARGS Parser for find operations
    """

    skip: Optional[int] = None
    limit: Optional[int] = None
    sort: Union[None, str, List[Tuple[str, SortDirection]]] = None

    @validator("sort")
    def name_must_contain_space(cls, v):
        if isinstance(v, str):
            return [(v, pymongo.ASCENDING)]
        return v


class InspectionStatuses(str, Enum):
    """
    Statuses of the collection inspection
    """

    FAIL = "FAIL"
    OK = "OK"


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
