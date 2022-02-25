import pytest

from beanie import init_beanie
from beanie.exceptions import MongoDBVersionError
from tests.odm.models import DocumentWithTimeseries


async def test_timeseries_collection(db):
    build_info = await db.command({"buildInfo": 1})
    mongo_version = build_info["version"]
    major_version = int(mongo_version.split(".")[0])
    if major_version < 5:
        with pytest.raises(MongoDBVersionError):
            await init_beanie(
                database=db, document_models=[DocumentWithTimeseries]
            )

    if major_version >= 5:
        await init_beanie(
            database=db, document_models=[DocumentWithTimeseries]
        )
        info = await db.command(
            {
                "listCollections": 1,
                "filter": {"name": "DocumentWithTimeseries"},
            }
        )

        assert info["cursor"]["firstBatch"][0] == {
            "name": "DocumentWithTimeseries",
            "type": "timeseries",
            "options": {
                "expireAfterSeconds": 2,
                "timeseries": {
                    "timeField": "ts",
                    "granularity": "seconds",
                    "bucketMaxSpanSeconds": 3600,
                },
            },
            "info": {"readOnly": False},
        }
