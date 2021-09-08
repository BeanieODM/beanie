from tests.odm.models import DocumentWithActions


async def test_before_insert():
    test_name = "test_name"
    sample = DocumentWithActions(name=test_name)
    await sample.insert()
    assert sample.name == 1
