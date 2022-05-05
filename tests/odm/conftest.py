from datetime import datetime, timedelta
from random import randint
from typing import List

import pytest

from beanie.odm.utils.general import init_beanie
from tests.odm.models import (
    DocumentTestModel,
    DocumentTestModelWithIndexFlagsAliases,
    SubDocument,
    DocumentTestModelWithCustomCollectionName,
    DocumentTestModelWithSimpleIndex,
    DocumentTestModelWithIndexFlags,
    DocumentTestModelWithComplexIndex,
    DocumentTestModelFailInspection,
    DocumentWithCustomIdUUID,
    DocumentWithCustomIdInt,
    DocumentWithCustomFiledsTypes,
    DocumentWithBsonEncodersFiledsTypes,
    DocumentWithActions,
    DocumentWithTurnedOnStateManagement,
    DocumentWithTurnedOnReplaceObjects,
    DocumentWithTurnedOffStateManagement,
    DocumentWithValidationOnSave,
    DocumentWithRevisionTurnedOn,
    DocumentWithPydanticConfig,
    House,
    Window,
    Door,
    Roof,
    InheritedDocumentWithActions,
    DocumentForEncodingTest,
    DocumentForEncodingTestDate,
    DocumentMultiModelOne,
    DocumentMultiModelTwo,
    DocumentUnion,
)
from tests.odm.views import TestView
from tests.odm.models import (
    Sample,
    Nested,
    Option2,
    Option1,
    GeoObject,
)


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


@pytest.fixture()
def sample_doc_not_saved(point):
    nested = Nested(
        integer=0,
        option_1=Option1(s="TEST"),
        union=Option1(s="TEST"),
        optional=None,
    )
    geo = GeoObject(
        coordinates=[
            point["longitude"],
            point["latitude"],
        ]
    )
    return Sample(
        timestamp=datetime.utcnow(),
        increment=0,
        integer=0,
        float_num=0,
        string="TEST_NOT_SAVED",
        nested=nested,
        optional=None,
        union=Option1(s="TEST"),
        geo=geo,
    )


@pytest.fixture()
async def session(cli, loop):
    s = await cli.start_session()
    yield s
    await s.end_session()


@pytest.fixture(autouse=True)
async def init(loop, db):
    models = [
        DocumentWithPydanticConfig,
        DocumentTestModel,
        DocumentTestModelWithCustomCollectionName,
        DocumentTestModelWithSimpleIndex,
        DocumentTestModelWithIndexFlags,
        DocumentTestModelWithIndexFlagsAliases,
        DocumentTestModelWithComplexIndex,
        DocumentTestModelFailInspection,
        DocumentWithBsonEncodersFiledsTypes,
        DocumentWithCustomFiledsTypes,
        DocumentWithCustomIdUUID,
        DocumentWithCustomIdInt,
        Sample,
        DocumentWithActions,
        DocumentWithTurnedOnStateManagement,
        DocumentWithTurnedOnReplaceObjects,
        DocumentWithTurnedOffStateManagement,
        DocumentWithValidationOnSave,
        DocumentWithRevisionTurnedOn,
        House,
        Window,
        Door,
        Roof,
        InheritedDocumentWithActions,
        DocumentForEncodingTest,
        DocumentForEncodingTestDate,
        TestView,
        DocumentMultiModelOne,
        DocumentMultiModelTwo,
        DocumentUnion,
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
        test_doc=SubDocument(test_str="foobar"),
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
                test_doc=SubDocument(test_str="foobar"),
                test_str="kipasa" if test_str is None else test_str,
            )
            for i in range(number)
        ]

    return generate_documents


@pytest.fixture
async def document(document_not_inserted, loop) -> DocumentTestModel:
    return await document_not_inserted.insert()


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
