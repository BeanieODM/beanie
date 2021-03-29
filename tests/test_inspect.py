from beanie.internal_models import InspectionStatuses
from tests.models import DocumentTestModel, DocumentTestModelFailInspection


async def test_inspect_ok(documents):
    await documents(10, "smth")
    result = await DocumentTestModel.inspect_collection()
    assert result.status == InspectionStatuses.OK
    assert result.errors == []


async def test_inspect_fail(documents):
    await documents(10, "smth")
    result = await DocumentTestModelFailInspection.inspect_collection()
    assert result.status == InspectionStatuses.FAIL
    assert len(result.errors) == 10
    assert (
        "1 validation error for DocumentTestModelFailInspection"
        in result.errors[0].error
    )
