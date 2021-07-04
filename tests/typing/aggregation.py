from typing import List, Dict, Any

from tests.typing.models import Test, ProjectionTest


async def aggregate() -> List[Dict[str, Any]]:
    result = await Test.aggregate([]).to_list()
    result_2 = await Test.find().aggregate([]).to_list()
    return result or result_2


async def aggregate_with_projection() -> List[ProjectionTest]:
    result = (
        await Test.find()
        .aggregate([], projection_model=ProjectionTest)
        .to_list()
    )
    result_2 = await Test.aggregate(
        [], projection_model=ProjectionTest
    ).to_list()
    return result or result_2
