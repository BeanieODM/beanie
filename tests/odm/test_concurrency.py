import asyncio

import motor.motor_asyncio

from beanie import Document, init_beanie


class SampleModel(Document):
    s: str = "TEST"
    i: int = 10


class SampleModel2(SampleModel):
    ...


class SampleModel3(SampleModel2):
    ...


class TestConcurrency:
    async def test_without_init(self, settings):
        for i in range(10):
            cli = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
            cli.get_io_loop = asyncio.get_running_loop
            db = cli[settings.mongodb_db_name]
            await init_beanie(
                db, document_models=[SampleModel3, SampleModel, SampleModel2]
            )

            async def insert_find():
                await SampleModel2().insert()
                docs = await SampleModel2.find(SampleModel2.i == 10).to_list()
                return docs

            await asyncio.gather(*[insert_find() for _ in range(10)])
        await SampleModel2.delete_all()
