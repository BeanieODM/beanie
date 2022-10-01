from tests.odm_sync.models import (
    SyncDocumentMultiModelOne,
    SyncDocumentMultiModelTwo,
    DocumentUnion,
)


class TestMultiModel:
    def test_multi_model(self):
        doc_1 = SyncDocumentMultiModelOne().insert()
        doc_2 = SyncDocumentMultiModelTwo().insert()

        new_doc_1 = SyncDocumentMultiModelOne.get(doc_1.id).run()
        new_doc_2 = SyncDocumentMultiModelTwo.get(doc_2.id).run()

        assert new_doc_1 is not None
        assert new_doc_2 is not None

        new_doc_1 = SyncDocumentMultiModelTwo.get(doc_1.id).run()
        new_doc_2 = SyncDocumentMultiModelOne.get(doc_2.id).run()

        assert new_doc_1 is None
        assert new_doc_2 is None

        new_docs_1 = SyncDocumentMultiModelOne.find({}).to_list()
        new_docs_2 = SyncDocumentMultiModelTwo.find({}).to_list()

        assert len(new_docs_1) == 1
        assert len(new_docs_2) == 1

        SyncDocumentMultiModelOne.update_all({"$set": {"shared": 100}}).run()

        new_doc_1 = SyncDocumentMultiModelOne.get(doc_1.id).run()
        new_doc_2 = SyncDocumentMultiModelTwo.get(doc_2.id).run()

        assert new_doc_1.shared == 100
        assert new_doc_2.shared == 0

    def test_union_doc(self):
        SyncDocumentMultiModelOne().insert()
        SyncDocumentMultiModelTwo().insert()
        SyncDocumentMultiModelOne().insert()
        SyncDocumentMultiModelTwo().insert()

        docs = DocumentUnion.all().to_list()
        assert isinstance(docs[0], SyncDocumentMultiModelOne)
        assert isinstance(docs[1], SyncDocumentMultiModelTwo)
        assert isinstance(docs[2], SyncDocumentMultiModelOne)
        assert isinstance(docs[3], SyncDocumentMultiModelTwo)

    def test_union_doc_aggregation(self):
        SyncDocumentMultiModelOne().insert()
        SyncDocumentMultiModelTwo().insert()
        SyncDocumentMultiModelOne().insert()
        SyncDocumentMultiModelTwo().insert()

        docs = DocumentUnion.aggregate(
            [{"$match": {"$expr": {"$eq": ["$int_filed", 0]}}}]
        ).to_list()
        assert len(docs) == 2

    def test_union_doc_link(self):
        doc_1 = SyncDocumentMultiModelOne().insert()
        SyncDocumentMultiModelTwo(linked_doc=doc_1).insert()

        docs = SyncDocumentMultiModelTwo.find({}, fetch_links=True).to_list()
        assert isinstance(docs[0].linked_doc, SyncDocumentMultiModelOne)
