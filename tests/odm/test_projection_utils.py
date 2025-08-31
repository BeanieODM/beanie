from beanie.odm.utils.projection import get_projection
from tests.odm.models import DocumentTestModel


async def test_get_projection():
    projection = get_projection(DocumentTestModel)
    assert projection == {
        "_id": 1,
        "test_int": 1,
        "test_list": 1,
        "test_str": 1,
        "test_doc": 1,
        "revision_id": 1,
    }
