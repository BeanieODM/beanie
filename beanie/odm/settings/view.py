from typing import List, Dict, Any, Union, Type, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, Field


class ViewSettingsInput(BaseModel):
    source: Union[str, Type]

    view_name: Optional[str]
    pipeline: List[Dict[str, Any]]

    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)


class ViewSettings(BaseModel):
    db: AsyncIOMotorDatabase
    view: AsyncIOMotorCollection

    source: Union[str, Type]

    view_name: str
    pipeline: List[Dict[str, Any]]

    bson_encoders: Dict[Any, Any]

    class Config:
        arbitrary_types_allowed = True
