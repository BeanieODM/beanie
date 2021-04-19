from random import randint
from typing import List

import pytest

from beanie.odm.general import init_beanie
from tests.odm.models import (
    DocumentTestModel,
    SubDocument,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithSimpleIndex,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelFailInspection,
)

object_storage = {}


@pytest.fixture()
async def session(cli, loop):
    s = await cli.start_session()
    yield s
    await s.end_session()


@pytest.fixture(autouse=True)
async def init(loop, db):
    models = [
        DocumentTestModel,
        DocumentTestModelWithCustomCollectionName,
        DocumentTestModelWithSimpleIndex,
        DocumentTestModelWithComplexIndex,
        DocumentTestModelFailInspection,
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
def document_not_inserted():
    return DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )


@pytest.fixture
def documents_not_inserted():
    def generate_documents(
        number: int, test_str: str = None, random: bool = False
    ) -> List[DocumentTestModel]:
        return [
            DocumentTestModel(
                test_int=randint(0, 1000000) if random else i,
                test_list=[
                    SubDocument(test_str="foo"),
                    SubDocument(test_str="bar"),
                ],
                test_str="kipasa" if test_str is None else test_str,
            )
            for i in range(number)
        ]

    return generate_documents


@pytest.fixture
async def document(document_not_inserted, loop) -> DocumentTestModel:
    return await document_not_inserted.create()


@pytest.fixture
def documents(documents_not_inserted):
    async def generate_documents(
        number: int, test_str: str = None, random: bool = False
    ):
        result = await DocumentTestModel.insert_many(
            documents_not_inserted(number, test_str, random)
        )
        return result.inserted_ids

    return generate_documents
