from tests.odm.models import TestDocumentWithRootModelAsAField


class TestRootModels:
    async def test_insert(self):
        doc = TestDocumentWithRootModelAsAField(pets=["dog", "cat", "fish"])
        await doc.insert()

        new_doc = await TestDocumentWithRootModelAsAField.get(doc.id)
        assert new_doc.pets.root == ["dog", "cat", "fish"]

        collection = TestDocumentWithRootModelAsAField.get_motor_collection()
        raw_doc = await collection.find_one({"_id": doc.id})
        assert raw_doc["pets"] == ["dog", "cat", "fish"]
