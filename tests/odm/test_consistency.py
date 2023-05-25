from beanie.odm.operators.update.general import Set
from tests.odm.models import (
    DocumentTestModel,
    DocumentWithTimeStampToTestConsistency,
)


class TestResponseOfTheChangingOperations:
    async def test_insert(self, document_not_inserted):
        result = await document_not_inserted.insert()
        assert isinstance(result, DocumentTestModel)

    async def test_update(self, document):
        result = await document.update(Set({"test_int": 43}))
        assert isinstance(result, DocumentTestModel)

    async def test_save(self, document, document_not_inserted):
        document.test_int = 43
        result = await document.save()
        assert isinstance(result, DocumentTestModel)

        document_not_inserted.test_int = 43
        result = await document_not_inserted.save()
        assert isinstance(result, DocumentTestModel)

    async def test_save_changes(self, document):
        document.test_int = 43
        result = await document.save_changes()
        assert isinstance(result, DocumentTestModel)

    async def test_replace(self, document):
        result = await document.replace()
        assert isinstance(result, DocumentTestModel)

    async def test_set(self, document):
        result = await document.set({"test_int": 43})
        assert isinstance(result, DocumentTestModel)

    async def test_inc(self, document):
        result = await document.inc({"test_int": 1})
        assert isinstance(result, DocumentTestModel)

    async def test_current_date(self):
        document = DocumentWithTimeStampToTestConsistency()
        await document.insert()
        result = await document.current_date({"ts": True})
        assert isinstance(result, DocumentWithTimeStampToTestConsistency)
