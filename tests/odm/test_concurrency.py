import asyncio

from pymongo import AsyncMongoClient

from beanie import Document, init_beanie


class SampleModel(Document):
    s: str = "TEST"
    i: int = 10


class SampleModel2(SampleModel): ...


class SampleModel3(SampleModel2): ...


class TestConcurrency:
    async def test_without_init(self, settings):
        clients = []
        for _ in range(10):
            client = AsyncMongoClient(settings.mongodb_dsn)
            clients.append(client)
            db = client[settings.mongodb_db_name]
            await init_beanie(
                db, document_models=[SampleModel3, SampleModel, SampleModel2]
            )

            async def insert_find():
                await SampleModel2().insert()
                docs = await SampleModel2.find(SampleModel2.i == 10).to_list()
                return docs

            await asyncio.gather(*[insert_find() for _ in range(10)])

        await SampleModel2.delete_all()

        [await client.close() for client in clients]
