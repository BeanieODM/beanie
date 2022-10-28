from beanie.odm.models import InspectionStatuses
from tests.sync.models import (
    DocumentTestModel,
    DocumentTestModelFailInspection,
)


def test_inspect_ok(documents):
    documents(10, "smth")
    result = DocumentTestModel.inspect_collection()
    assert result.status == InspectionStatuses.OK
    assert result.errors == []


def test_inspect_fail(documents):
    documents(10, "smth")
    result = DocumentTestModelFailInspection.inspect_collection()
    assert result.status == InspectionStatuses.FAIL
    assert len(result.errors) == 10
    assert (
        "1 validation error for DocumentTestModelFailInspection"
        in result.errors[0].error
    )


def test_inspect_ok_with_session(documents, session):
    documents(10, "smth")
    result = DocumentTestModel.inspect_collection(session=session)
    assert result.status == InspectionStatuses.OK
    assert result.errors == []
