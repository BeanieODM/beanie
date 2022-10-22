from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel


class Granularity(str, Enum):
    """
    Time Series Granuality
    """

    seconds = "seconds"
    minutes = "minutes"
    hours = "hours"


class TimeSeriesConfig(BaseModel):
    """
    Time Series Collection config
    """

    time_field: str
    meta_field: Optional[str]
    granularity: Optional[Granularity]
    expire_after_seconds: Optional[float]

    def build_query(self, collection_name: str) -> Dict[str, Any]:
        res: Dict[str, Any] = {"name": collection_name}
        timeseries = {"timeField": self.time_field}
        if self.meta_field is not None:
            timeseries["metaField"] = self.meta_field
        if self.granularity is not None:
            timeseries["granularity"] = self.granularity
        res["timeseries"] = timeseries
        if self.expire_after_seconds is not None:
            res["expireAfterSeconds"] = self.expire_after_seconds
        return res
