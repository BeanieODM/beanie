from enum import Enum
from typing import List, Optional, Union, Tuple

import pymongo
from pydantic import BaseModel, validator

from beanie.odm.fields import PydanticObjectId


class SortDirection(int, Enum):
    ASCENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING


class FindOperationKWARGS(BaseModel):
    skip: Optional[int] = None
    limit: Optional[int] = None
    sort: Union[None, str, List[Tuple[str, SortDirection]]] = None

    @validator("sort")
    def name_must_contain_space(cls, v):
        if isinstance(v, str):
            return [(v, pymongo.ASCENDING)]
        return v


class InspectionStatuses(str, Enum):
    FAIL = "FAIL"
    OK = "OK"


class InspectionError(BaseModel):
    document_id: PydanticObjectId
    error: str


class InspectionResult(BaseModel):
    status: InspectionStatuses = InspectionStatuses.OK
    errors: List[InspectionError] = []
