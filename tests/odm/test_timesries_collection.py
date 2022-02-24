async def test_timeseries_collection(db):
    info = await db.command(
        {"listCollections": 1, "filter": {"name": "DocumentWithTimeseries"}}
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
