from tests.sync.models import (
    DocumentMultiModelOne,
    DocumentMultiModelTwo,
    DocumentUnion,
)


class TestMultiModel:
    def test_multi_model(self):
        doc_1 = DocumentMultiModelOne().insert()
        doc_2 = DocumentMultiModelTwo().insert()

        new_doc_1 = DocumentMultiModelOne.get(doc_1.id).run()
        new_doc_2 = DocumentMultiModelTwo.get(doc_2.id).run()

        assert new_doc_1 is not None
        assert new_doc_2 is not None

        new_doc_1 = DocumentMultiModelTwo.get(doc_1.id).run()
        new_doc_2 = DocumentMultiModelOne.get(doc_2.id).run()

        assert new_doc_1 is None
        assert new_doc_2 is None

        new_docs_1 = DocumentMultiModelOne.find({}).to_list()
        new_docs_2 = DocumentMultiModelTwo.find({}).to_list()

        assert len(new_docs_1) == 1
        assert len(new_docs_2) == 1

        DocumentMultiModelOne.update_all({"$set": {"shared": 100}}).run()

        new_doc_1 = DocumentMultiModelOne.get(doc_1.id).run()
        new_doc_2 = DocumentMultiModelTwo.get(doc_2.id).run()

        assert new_doc_1.shared == 100
        assert new_doc_2.shared == 0

    def test_union_doc(self):
        DocumentMultiModelOne().insert()
        DocumentMultiModelTwo().insert()
        DocumentMultiModelOne().insert()
        DocumentMultiModelTwo().insert()

        docs = DocumentUnion.all().to_list()
        assert isinstance(docs[0], DocumentMultiModelOne)
        assert isinstance(docs[1], DocumentMultiModelTwo)
        assert isinstance(docs[2], DocumentMultiModelOne)
        assert isinstance(docs[3], DocumentMultiModelTwo)

    def test_union_doc_aggregation(self):
        DocumentMultiModelOne().insert()
        DocumentMultiModelTwo().insert()
        DocumentMultiModelOne().insert()
        DocumentMultiModelTwo().insert()

        docs = DocumentUnion.aggregate(
            [{"$match": {"$expr": {"$eq": ["$int_filed", 0]}}}]
        ).to_list()
        assert len(docs) == 2

    def test_union_doc_link(self):
        doc_1 = DocumentMultiModelOne().insert()
        DocumentMultiModelTwo(linked_doc=doc_1).insert()

        docs = DocumentMultiModelTwo.find({}, fetch_links=True).to_list()
        assert isinstance(docs[0].linked_doc, DocumentMultiModelOne)
