from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentWithRootModelAsAField

if IS_PYDANTIC_V2:

    class TestRootModels:
        async def test_insert(self):
            doc = DocumentWithRootModelAsAField(pets=["dog", "cat", "fish"])
            await doc.insert()

            new_doc = await DocumentWithRootModelAsAField.get(doc.id)
            assert new_doc.pets.root == ["dog", "cat", "fish"]

            collection = DocumentWithRootModelAsAField.get_motor_collection()
            raw_doc = await collection.find_one({"_id": doc.id})
            assert raw_doc["pets"] == ["dog", "cat", "fish"]
