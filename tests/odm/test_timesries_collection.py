async def test_timeseries_collection(db):
    build_info = await db.command({"buildInfo": 1})
    mongo_version = build_info["version"]
    major_version = int(mongo_version.split(".")[0])

    if major_version >= 5:
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
