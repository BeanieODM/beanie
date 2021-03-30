from enum import Enum
from typing import List, Optional

from pydantic.main import BaseModel

from beanie import Document


class MigrationStatuses(str, Enum):
    STARTED = "STARTED"
    OK = "OK"
    FAIL = "FAIL"


class Migration(Document):
    name: str
    is_current: bool
    status: MigrationStatuses = MigrationStatuses.STARTED


class RunningDirections(str, Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"


class RunningMode(BaseModel):
    direction: RunningDirections
    distance: int = 0


class ParsedMigrations(BaseModel):
    path: str
    names: List[str]
    current: Optional[Migration] = None
