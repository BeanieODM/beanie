# Time Series

MongoDB 5.0+ supports native time series collections, which are optimised for
storing sequences of measurements over time.  Beanie exposes this feature
through the `TimeSeriesConfig` class.

> **Requirements**
>
> - MongoDB 5.0 or higher for basic time series support.
> - MongoDB 6.3 or higher for `bucket_max_span_seconds` and
>   `bucket_rounding_seconds`.

---

## Defining a Time Series Document

Configure a time series collection via the `Settings.timeseries` attribute:

```python
from datetime import datetime

from beanie import Document, TimeSeriesConfig, Granularity
from pydantic import Field


class SensorReading(Document):
    # Required: the field MongoDB uses to bucket measurements by time
    ts: datetime = Field(default_factory=datetime.utcnow)
    # Optional metadata field (acts like a "series key" or "tag")
    sensor_id: str
    # Measurement value
    temperature: float

    class Settings:
        name = "sensor_readings"
        timeseries = TimeSeriesConfig(
            time_field="ts",              # Required — must be a datetime field
            meta_field="sensor_id",       # Optional — used to identify each series
            granularity=Granularity.seconds,  # Optional — hours | minutes | seconds
            expire_after_seconds=86400,   # Optional — TTL: auto-delete after 1 day
        )
```

### `TimeSeriesConfig` Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `time_field` | `str` | Yes | Name of the `datetime` field used for bucketing |
| `meta_field` | `str` | No | Name of the field identifying the time series (e.g. device ID) |
| `granularity` | `Granularity` | No | Bucketing granularity: `hours`, `minutes`, or `seconds` |
| `expire_after_seconds` | `int` | No | TTL in seconds; documents older than this are deleted automatically |
| `bucket_max_span_seconds` | `int` | No | Maximum time span per bucket (MongoDB 6.3+) |
| `bucket_rounding_seconds` | `int` | No | Rounding applied to bucket boundaries (MongoDB 6.3+) |

---

## Inserting Measurements

Time series documents are inserted the same way as regular Beanie documents:

```python
import asyncio
from datetime import datetime, timedelta

import motor.motor_asyncio
from beanie import init_beanie


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.my_db, document_models=[SensorReading])

    # Insert a single reading
    reading = SensorReading(sensor_id="sensor-1", temperature=22.4)
    await reading.insert()

    # Insert many readings at once
    readings = [
        SensorReading(
            ts=datetime.utcnow() - timedelta(minutes=i),
            sensor_id="sensor-1",
            temperature=20.0 + i * 0.5,
        )
        for i in range(10)
    ]
    await SensorReading.insert_many(readings)
```

> **Note:** Time series collections do **not** support updating or deleting
> individual documents — they are append-only by design.  Use
> `expire_after_seconds` for automatic cleanup.

---

## Querying Time Series Data

Query a time series collection exactly like a regular collection:

```python
from beanie.odm.operators.find.comparison import GTE, LTE

# All readings from the last hour
one_hour_ago = datetime.utcnow() - timedelta(hours=1)
recent = await SensorReading.find(
    SensorReading.ts >= one_hour_ago
).sort(+SensorReading.ts).to_list()

# Readings for a specific sensor
sensor_data = await SensorReading.find(
    SensorReading.sensor_id == "sensor-1"
).to_list()
```

### Aggregation Example

```python
from pydantic import BaseModel, Field


class HourlyAverage(BaseModel):
    hour: str = Field(alias="_id")
    avg_temp: float


hourly = await SensorReading.find(
    SensorReading.sensor_id == "sensor-1"
).aggregate(
    [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%dT%H:00",
                        "date": "$ts",
                    }
                },
                "avg_temp": {"$avg": "$temperature"},
            }
        },
        {"$sort": {"_id": 1}},
    ],
    projection_model=HourlyAverage,
).to_list()

for h in hourly:
    print(f"{h.hour}: {h.avg_temp:.1f}°C")
```

---

## Granularity Guide

Choose `granularity` based on how frequently you insert data:

| Data frequency | Recommended granularity |
|---|---|
| Multiple times per minute | `seconds` |
| Once per minute to once per hour | `minutes` |
| Less than once per hour | `hours` |

Setting the correct granularity allows MongoDB to store data more efficiently
in its internal bucket structure.

---

## Limitations

- Time series collections are **append-only**: individual document updates and
  deletes are not supported.
- The `time_field` must be a `datetime` (not `date` or `int`).
- Time series collections cannot be converted to regular collections (or vice
  versa) after creation.
- `BulkWriter` is supported for inserts but not for updates or deletes.
