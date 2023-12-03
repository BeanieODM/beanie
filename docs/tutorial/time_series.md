# Time series

You can set up a timeseries collection using the inner `Settings` class.

**Be aware, timeseries collections a supported by MongoDB 5.0 and higher only. The fields `bucket_max_span_seconds` and `bucket_rounding_seconds` however require MongoDB 6.3 or higher**

```python
from datetime import datetime

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field


class Sample(Document):
    ts: datetime = Field(default_factory=datetime.now)
    meta: str

    class Settings:
        timeseries = TimeSeriesConfig(
            time_field="ts", #  Required
            meta_field="meta", #  Optional
            granularity=Granularity.hours, #  Optional
            bucket_max_span_seconds=3600,  #  Optional
            bucket_rounding_seconds=3600,  #  Optional
            expire_after_seconds=2  #  Optional
        )
```

TimeSeriesConfig fields reflect the respective parameters of the MongoDB timeseries creation function.

MongoDB documentation: https://docs.mongodb.com/manual/core/timeseries-collections/