from typing import TypeVar

from pydantic import BaseModel

ProjectionType = TypeVar("ProjectionType", bound=BaseModel)
