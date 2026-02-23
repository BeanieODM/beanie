from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentWithRootModelAsAField

if IS_PYDANTIC_V2:
    from tests.odm.models import DocumentWithCustomIterRootModel

    class TestRootModels:
        async def test_insert(self):
            doc = DocumentWithRootModelAsAField(pets=["dog", "cat", "fish"])
            await doc.insert()

            new_doc = await DocumentWithRootModelAsAField.get(doc.id)
            assert new_doc.pets.root == ["dog", "cat", "fish"]

            collection = DocumentWithRootModelAsAField.get_pymongo_collection()
            raw_doc = await collection.find_one({"_id": doc.id})
            assert raw_doc["pets"] == ["dog", "cat", "fish"]

        async def test_save_with_custom_iter_rootmodel(self):
            """RootModel with custom __iter__ must not break save().

            Regression test for https://github.com/BeanieODM/beanie/issues/830.
            """
            doc = await DocumentWithCustomIterRootModel(
                items=[1, 2, 3]
            ).insert()
            doc.items.root.append(4)
            await doc.save()

            reloaded = await DocumentWithCustomIterRootModel.get(doc.id)
            assert reloaded.items.root == [1, 2, 3, 4]
