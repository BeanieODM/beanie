import warnings
from typing import Optional, Type, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import Field
from pymongo import IndexModel

from beanie.exceptions import MongoDBVersionError
from beanie.odm.settings.base import ItemSettings
from beanie.odm.settings.timeseries import TimeSeriesConfig


class IndexModelField(IndexModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, IndexModel):
            return v
        else:
            return IndexModel(v)


class DocumentSettings(ItemSettings):
    use_state_management: bool = False
    state_management_replace_objects: bool = False
    validate_on_save: bool = False
    use_revision: bool = False
    single_root_inheritance: bool = False

    indexes: List[IndexModelField] = Field(default_factory=list)
    timeseries: Optional[TimeSeriesConfig] = None

    @classmethod
    def init(
        cls,
        database: AsyncIOMotorDatabase,
        document_model: Type,
        allow_index_dropping: bool,
    ) -> "DocumentSettings":

        settings_class = getattr(document_model, "Settings", None)
        settings_vars = (
            {} if settings_class is None else dict(vars(settings_class))
        )

        # ------------------------------------ #

    class Config:
        arbitrary_types_allowed = True
