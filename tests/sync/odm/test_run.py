from beanie import PydanticObjectId
from tests.sync.models import DocumentTestModel, Sample


class TestRun:
    def test_get(self, document):
        new_document = DocumentTestModel.get(document.id).run()
        assert new_document == document

        new_document = ~DocumentTestModel.get(document.id)
        assert new_document == document

    def test_find_many(self, preset_documents):
        result = ~Sample.find_many(Sample.integer > 1).find_many(
            Sample.nested.optional == None
        )
        assert len(result) == 2
        for a in result:
            assert a.integer > 1
            assert a.nested.optional is None

    def test_find_many_skip(self, preset_documents):
        q = Sample.find_many(Sample.integer > 1, skip=2)
        assert q.skip_number == 2

        q = Sample.find_many(Sample.integer > 1).skip(2)
        assert q.skip_number == 2

        result = (
            ~Sample.find_many(Sample.increment > 2)
            .find_many(Sample.nested.optional == None)
            .skip(1)
        )
        assert len(result) == 3
        for sample in result:
            assert sample.increment > 2
            assert sample.nested.optional is None

    def test_find_one(self, documents):
        inserted_one = documents(1, "kipasa")
        documents(10, "smthe else")
        expected_doc_id = PydanticObjectId(inserted_one[0])
        new_document = ~DocumentTestModel.find_one({"test_str": "kipasa"})
        assert new_document.id == expected_doc_id

    def test_find_all(self, documents):
        documents(4, "uno")
        documents(2, "dos")
        documents(1, "cuatro")
        result = ~DocumentTestModel.find_all()
        assert len(result) == 7

    def test_update_one(self, document):
        ~DocumentTestModel.find_one(
            {"_id": document.id, "test_list.test_str": "foo"}
        ).update({"$set": {"test_list.$.test_str": "foo_foo"}})
        new_document = ~DocumentTestModel.get(document.id)
        assert new_document.test_list[0].test_str == "foo_foo"

    def test_update_many(self, documents):
        documents(10, "foo")
        documents(7, "bar")
        ~DocumentTestModel.find_many({"test_str": "foo"}).update(
            {"$set": {"test_str": "bar"}}
        )
        bar_documetns = ~DocumentTestModel.find_many({"test_str": "bar"})
        assert len(bar_documetns) == 17
        foo_documetns = ~DocumentTestModel.find_many({"test_str": "foo"})
        assert len(foo_documetns) == 0

    def test_update_all(self, documents):
        documents(10, "foo")
        documents(7, "bar")
        ~DocumentTestModel.update_all(
            {"$set": {"test_str": "smth_else"}},
        )
        bar_documetns = ~DocumentTestModel.find_many({"test_str": "bar"})
        assert len(bar_documetns) == 0
        foo_documetns = ~DocumentTestModel.find_many({"test_str": "foo"})
        assert len(foo_documetns) == 0
        smth_else_documetns = ~DocumentTestModel.find_many(
            {"test_str": "smth_else"}
        )
        assert len(smth_else_documetns) == 17

    def test_delete_one(self, documents):
        documents(4, "uno")
        documents(2, "dos")
        documents(1, "cuatro")
        ~DocumentTestModel.find_one({"test_str": "uno"}).delete()
        documents = DocumentTestModel.find_all().to_list()
        assert len(documents) == 6

    def test_delete_many(self, documents):
        documents(4, "uno")
        documents(2, "dos")
        documents(1, "cuatro")
        ~DocumentTestModel.find_many({"test_str": "uno"}).delete()
        documents = DocumentTestModel.find_all().to_list()
        assert len(documents) == 3
