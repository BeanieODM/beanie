from datetime import datetime, timedelta

import pytest

from beanie import init_beanie
from tests.odm.query_builder.models import (
    Sample,
    Nested,
    Option2,
    Option1,
    GeoObject,
)


@pytest.fixture(autouse=True)
async def init(loop, db):
    models = [
        Sample,
    ]
    await init_beanie(
        database=db,
        document_models=models,
    )
    yield None

    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()


@pytest.fixture
def point():
    return {
        "longitude": 13.404954,
        "latitude": 52.520008,
    }


@pytest.fixture
async def preset_documents(point):
    docs = []
    for i in range(10):
        timestamp = datetime.utcnow() - timedelta(days=i)
        integer_1: int = i // 3
        integer_2: int = i // 2
        float_num = integer_1 + 0.3
        string: str = f"test_{integer_1}"
        option_1 = Option1(s="TEST")
        option_2 = Option2(f=3.14)
        union = option_1 if i % 2 else option_2
        optional = option_2 if not i % 3 else None
        geo = GeoObject(
            coordinates=[
                point["longitude"] + i / 10,
                point["latitude"] + i / 10,
            ]
        )
        nested = Nested(
            integer=integer_2,
            option_1=option_1,
            union=union,
            optional=optional,
        )

        sample = Sample(
            timestamp=timestamp,
            increment=i,
            integer=integer_1,
            float_num=float_num,
            string=string,
            nested=nested,
            optional=optional,
            union=union,
            geo=geo,
        )
        docs.append(sample)
    await Sample.insert_many(documents=docs)
