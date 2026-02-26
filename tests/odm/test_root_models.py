from tests.odm.models import DocumentWithRootModelAsAField


class TestRootModels:
    async def test_insert(self):
        doc = DocumentWithRootModelAsAField(pets=["dog", "cat", "fish"])
        await doc.insert()

        new_doc = await DocumentWithRootModelAsAField.get(doc.id)
        assert new_doc.pets.root == ["dog", "cat", "fish"]

        collection = DocumentWithRootModelAsAField.get_pymongo_collection()
        raw_doc = await collection.find_one({"_id": doc.id})
        assert raw_doc["pets"] == ["dog", "cat", "fish"]
