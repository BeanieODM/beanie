from typing import List, Dict, Any, Optional

from pydantic import BaseModel

from beanie import Document


class Test(Document):
    foo: str
    bar: str
    baz: str


class ProjectionTest(BaseModel):
    foo: str
    bar: int


async def get_test_multi() -> List[Test]:
    return await Test.find().to_list()


async def get_test_multi_pr() -> List[ProjectionTest]:
    return await Test.find().project(projection_model=ProjectionTest).to_list()


async def get_test_multi_generator() -> List[Test]:
    docs: List[Test] = []
    async for doc in Test.find():
        docs.append(doc)
    return docs


async def get_test_multi_pr_generator() -> List[ProjectionTest]:
    docs: List[ProjectionTest] = []
    async for doc in Test.find().project(projection_model=ProjectionTest):
        docs.append(doc)
    return docs


async def get_test_single() -> Optional[Test]:
    t = await Test.find_one()
    if t is not None:
        t1: Test = t
        print(t1)
    return t


async def get_test_single_pr() -> Optional[ProjectionTest]:
    doc = await Test.find_one().project(projection_model=ProjectionTest)
    if doc is not None:
        doc_1: ProjectionTest = doc
        print(doc_1)
    return doc


async def aggregate_test() -> List[Dict[str, Any]]:
    result = await Test.aggregate([]).to_list()
    result_2 = await Test.find().aggregate([]).to_list()
    return result or result_2


async def aggregate_test_pr() -> List[ProjectionTest]:
    result = (
        await Test.find()
        .aggregate([], projection_model=ProjectionTest)
        .to_list()
    )
    result_2 = await Test.aggregate(
        [], projection_model=ProjectionTest
    ).to_list()
    return result or result_2
