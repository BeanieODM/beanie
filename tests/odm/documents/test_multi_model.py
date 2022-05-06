from tests.odm.models import (
    DocumentMultiModelOne,
    DocumentMultiModelTwo,
    DocumentUnion,
)


class TestMultiModel:
    async def test_multi_model(self):
        doc_1 = await DocumentMultiModelOne().insert()
        doc_2 = await DocumentMultiModelTwo().insert()

        new_doc_1 = await DocumentMultiModelOne.get(doc_1.id)
        new_doc_2 = await DocumentMultiModelTwo.get(doc_2.id)

        assert new_doc_1 is not None
        assert new_doc_2 is not None

        new_doc_1 = await DocumentMultiModelTwo.get(doc_1.id)
        new_doc_2 = await DocumentMultiModelOne.get(doc_2.id)

        assert new_doc_1 is None
        assert new_doc_2 is None

        new_docs_1 = await DocumentMultiModelOne.find({}).to_list()
        new_docs_2 = await DocumentMultiModelTwo.find({}).to_list()

        assert len(new_docs_1) == 1
        assert len(new_docs_2) == 1

        await DocumentMultiModelOne.update_all({"$set": {"shared": 100}})

        new_doc_1 = await DocumentMultiModelOne.get(doc_1.id)
        new_doc_2 = await DocumentMultiModelTwo.get(doc_2.id)

        assert new_doc_1.shared == 100
        assert new_doc_2.shared == 0

    async def test_union_doc(self):
        await DocumentMultiModelOne().insert()
        await DocumentMultiModelTwo().insert()
        await DocumentMultiModelOne().insert()
        await DocumentMultiModelTwo().insert()

        docs = await DocumentUnion.all().to_list()
        assert isinstance(docs[0], DocumentMultiModelOne)
        assert isinstance(docs[1], DocumentMultiModelTwo)
        assert isinstance(docs[2], DocumentMultiModelOne)
        assert isinstance(docs[3], DocumentMultiModelTwo)

    async def test_union_doc_aggregation(self):
        await DocumentMultiModelOne().insert()
        await DocumentMultiModelTwo().insert()
        await DocumentMultiModelOne().insert()
        await DocumentMultiModelTwo().insert()

        docs = await DocumentUnion.aggregate(
            [{"$match": {"$expr": {"$eq": ["$int_filed", 0]}}}]
        ).to_list()
        assert len(docs) == 2

    async def test_union_doc_link(self):
        doc_1 = await DocumentMultiModelOne().insert()
        await DocumentMultiModelTwo(linked_doc=doc_1).insert()

        docs = await DocumentMultiModelTwo.find({}, fetch_links=True).to_list()
        assert isinstance(docs[0].linked_doc, DocumentMultiModelOne)
