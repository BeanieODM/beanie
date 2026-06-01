from beanie.odm.operators.find.logical import And, Nor, Or
from tests.typing.models import ProjectionTest, Test


async def find_many() -> list[Test]:
    return await Test.find().to_list()


async def find_many_with_projection() -> list[ProjectionTest]:
    return await Test.find().project(projection_model=ProjectionTest).to_list()


async def find_many_generator() -> list[Test]:
    docs: list[Test] = []
    async for doc in Test.find():
        docs.append(doc)
    return docs


async def find_many_generator_with_projection() -> list[ProjectionTest]:
    docs: list[ProjectionTest] = []
    async for doc in Test.find().project(projection_model=ProjectionTest):
        docs.append(doc)
    return docs


async def find_one() -> Test | None:
    return await Test.find_one()


async def find_one_with_projection() -> ProjectionTest | None:
    return await Test.find_one().project(projection_model=ProjectionTest)


def logical_operators_accept_comparisons() -> None:
    Or(Test.foo == "bar", Test.baz == "qux")
    And(Test.foo == "bar", Test.baz == "qux")
    Nor(Test.foo == "bar", Test.baz == "qux")

    Or(Test.foo == "bar", Test.baz > "a")
