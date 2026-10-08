import pytest

from beanie import init_beanie
from beanie.exceptions import MongoDBVersionError
from tests.odm.models import (
    DocumentWithTimeseries,
    HumidityMeasurement,
    MeasurementWithTimeseries,
    TemperatureMeasurement,
)


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


async def test_timeseries_polymorphic_collection(db):
    build_info = await db.command({"buildInfo": 1})
    mongo_version = build_info["version"]
    major_version = int(mongo_version.split(".")[0])
    if major_version < 5:
        with pytest.raises(MongoDBVersionError):
            await init_beanie(
                database=db,
                document_models=[
                    MeasurementWithTimeseries,
                    TemperatureMeasurement,
                    HumidityMeasurement,
                ],
            )

    if major_version >= 5:
        await db.drop_collection("measurements")
        await init_beanie(
            database=db,
            document_models=[
                MeasurementWithTimeseries,
                TemperatureMeasurement,
                HumidityMeasurement,
            ],
        )
        info = await db.command(
            {
                "listCollections": 1,
                "filter": {"name": "measurements"},
            }
        )
        assert info["cursor"]["firstBatch"][0] == {
            "name": "measurements",
            "type": "timeseries",
            "options": {
                "timeseries": {
                    "timeField": "ts",
                    "granularity": "seconds",
                    "bucketMaxSpanSeconds": 3600,
                },
            },
            "info": {"readOnly": False},
        }


async def test_timeseries_polymorphic_collection_created_once(db):
    build_info = await db.command({"buildInfo": 1})
    major_version = int(build_info["version"].split(".")[0])
    if major_version < 5:
        pytest.skip("Timeseries require MongoDB 5 or higher")

    await db.drop_collection("measurements")

    # `MeasurementWithTimeseries` and its two subclasses all share the
    # "measurements" collection. Only the first one processed should call
    # `create_collection`; the others must see it in the cache and reuse it,
    # otherwise the second call raises CollectionInvalid.
    original_create_collection = db.create_collection
    created_names = []

    async def counting_create_collection(name, *args, **kwargs):
        created_names.append(name)
        return await original_create_collection(name, *args, **kwargs)

    db.create_collection = counting_create_collection
    try:
        await init_beanie(
            database=db,
            document_models=[
                MeasurementWithTimeseries,
                TemperatureMeasurement,
                HumidityMeasurement,
            ],
        )
    finally:
        db.create_collection = original_create_collection

    assert created_names == ["measurements"]

    temperature = await TemperatureMeasurement(temperature=21.5).insert()
    humidity = await HumidityMeasurement(humidity=55.0).insert()

    found_by_id = {
        doc.id: doc
        for doc in await MeasurementWithTimeseries.find(
            with_children=True
        ).to_list()
    }

    found_temperature = found_by_id[temperature.id]
    found_humidity = found_by_id[humidity.id]
    assert isinstance(found_temperature, TemperatureMeasurement)
    assert isinstance(found_humidity, HumidityMeasurement)
    assert found_temperature.temperature == 21.5
    assert found_humidity.humidity == 55.0
