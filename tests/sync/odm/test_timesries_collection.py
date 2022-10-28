import pytest

from beanie.sync import init_beanie
from beanie.exceptions import MongoDBVersionError
from tests.sync.models import DocumentWithTimeseries


def test_timeseries_collection(db):
    build_info = db.command({"buildInfo": 1})
    mongo_version = build_info["version"]
    major_version = int(mongo_version.split(".")[0])
    if major_version < 5:
        with pytest.raises(MongoDBVersionError):
            init_beanie(database=db, document_models=[DocumentWithTimeseries])

    if major_version >= 5:
        init_beanie(database=db, document_models=[DocumentWithTimeseries])
        info = db.command(
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
