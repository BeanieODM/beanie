import pytest

from beanie import init_beanie
from tests.odm.query_builder.models import A, B, D, C


@pytest.fixture(autouse=True)
async def init(loop, db):
    models = [
        A,
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
async def preset_documents():
    docs = []
    for i in range(10):
        d = D(f=i + 0.3)
        c = C(d=d, s="test")
        c_d = c if i % 2 == 0 else d
        o_d = d if i % 2 == 1 else None
        b = B(i=i / 3, c=c, c_d=c_d, o_d=o_d)
        a = A(i=i / 2, c=c, c_d=c_d, o_d=o_d, b=b)
        docs.append(a)

    await A.insert_many(documents=docs)
