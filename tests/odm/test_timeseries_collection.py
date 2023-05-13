import pytest

from beanie import init_beanie
from beanie.exceptions import MongoDBVersionError
from beanie.odm.utils.compatibility import supports_timeseries
from beanie.odm.utils.general import DatabaseVersion
from tests.odm.models import DocumentWithTimeseries


async def test_timeseries_collection(db, database_version: DatabaseVersion):
    if not supports_timeseries(database_version):
        with pytest.raises(MongoDBVersionError):
            await init_beanie(
                database=db, document_models=[DocumentWithTimeseries]
            )

    if supports_timeseries(database_version):
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
