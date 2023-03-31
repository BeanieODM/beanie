import pytest
from bson import ObjectId

from beanie import PydanticObjectId, WriteRules
from beanie.exceptions import StateManagementIsTurnedOff, StateNotSaved
from beanie.odm.utils.parsing import parse_obj
from tests.odm.models import (
    DocumentWithTurnedOffStateManagement,
    DocumentWithTurnedOnReplaceObjects,
    DocumentWithTurnedOnStateManagement,
    DocumentWithTurnedOnSavePrevious,
    HouseWithRevision,
    InternalDoc,
    LockWithRevision,
    WindowWithRevision,
    StateAndDecimalFieldModel,
    DocumentWithTurnedOnStateManagementWithCustomId,
)


@pytest.fixture
def state():
    return {
        "num_1": 1,
        "num_2": 2,
        "_id": ObjectId(),
        "internal": InternalDoc(),
    }


@pytest.fixture
def state_without_id():
    return {
        "num_1": 1,
        "num_2": 2,
        "internal": InternalDoc(),
    }


@pytest.fixture
def doc_default(state):
    return parse_obj(DocumentWithTurnedOnStateManagement, state)


@pytest.fixture
def doc_replace(state):
    return parse_obj(DocumentWithTurnedOnReplaceObjects, state)


@pytest.fixture
def doc_previous(state):
    return parse_obj(DocumentWithTurnedOnSavePrevious, state)


@pytest.fixture
async def saved_doc_default(doc_default):
    await doc_default.insert()
    return doc_default


@pytest.fixture
async def saved_doc_previous(doc_previous):
    await doc_previous.insert()
    return doc_previous


@pytest.fixture
def windows_not_inserted():
    return [
        WindowWithRevision(x=10, y=10, lock=LockWithRevision(k=10)),
        WindowWithRevision(x=11, y=11, lock=LockWithRevision(k=11)),
    ]


@pytest.fixture
def house_not_inserted(windows_not_inserted):
    return HouseWithRevision(windows=windows_not_inserted)


@pytest.fixture
async def house(house_not_inserted):
    return await house_not_inserted.insert(link_rule=WriteRules.WRITE)


class TestStateManagement:
    async def test_use_state_management_property(self):
        assert (
            DocumentWithTurnedOnStateManagement.use_state_management() is True
        )
        assert (
            DocumentWithTurnedOffStateManagement.use_state_management()
            is False
        )

    async def test_state_with_decimal_field(
        self,
    ):
        await StateAndDecimalFieldModel(amt=10.01).insert()
        await StateAndDecimalFieldModel.all().to_list()

    async def test_parse_object_with_saving_state(self):
        obj = {
            "num_1": 1,
            "num_2": 2,
            "_id": ObjectId(),
            "internal": InternalDoc(),
        }
        doc = parse_obj(DocumentWithTurnedOnStateManagement, obj)
        assert doc.get_saved_state() == obj
        assert doc.get_previous_saved_state() is None

    class TestSaveState:
        async def test_save_state(self):
            doc = DocumentWithTurnedOnStateManagement(
                num_1=1, num_2=2, internal=InternalDoc(num=1, string="s")
            )
            assert doc.get_saved_state() is None
            assert doc.get_previous_saved_state() is None

            doc.id = PydanticObjectId()
            doc._save_state()
            assert doc.get_saved_state() == {
                "num_1": 1,
                "num_2": 2,
                "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
                "_id": doc.id,
            }
            assert doc.get_previous_saved_state() is None

            doc.num_1 = 2
            doc.num_2 = 3
            doc._save_state()
            assert doc.get_saved_state() == {
                "num_1": 2,
                "num_2": 3,
                "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
                "_id": doc.id,
            }
            assert doc.get_previous_saved_state() is None

        async def test_save_state_with_custom_id_type(self):
            doc = DocumentWithTurnedOnStateManagementWithCustomId(
                id=0,
                num_1=1,
                num_2=2,
            )
            with pytest.raises(StateNotSaved):
                await doc.save_changes()
            doc.num_1 = 2
            with pytest.raises(StateNotSaved):
                await doc.save_changes()

        async def test_save_state_with_previous(self):
            doc = DocumentWithTurnedOnSavePrevious(
                num_1=1, num_2=2, internal=InternalDoc(num=1, string="s")
            )
            assert doc.get_saved_state() is None
            assert doc.get_previous_saved_state() is None

            doc.id = PydanticObjectId()
            doc._save_state()
            assert doc.get_saved_state() == {
                "num_1": 1,
                "num_2": 2,
                "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
                "_id": doc.id,
            }
            assert doc.get_previous_saved_state() is None

            doc.num_1 = 2
            doc.num_2 = 3
            doc._save_state()
            assert doc.get_saved_state() == {
                "num_1": 2,
                "num_2": 3,
                "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
                "_id": doc.id,
            }
            assert doc.get_previous_saved_state() == {
                "num_1": 1,
                "num_2": 2,
                "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
                "_id": doc.id,
            }

    class TestIsChanged:
        async def test_state_management_off(self):
            doc = DocumentWithTurnedOffStateManagement(num_1=1, num_2=2)

            with pytest.raises(StateManagementIsTurnedOff):
                doc.is_changed

        async def test_state_management_on_not_changed(self):
            doc = DocumentWithTurnedOnStateManagement(
                num_1=1, num_2=2, internal=InternalDoc()
            )

            with pytest.raises(StateNotSaved):
                doc.is_changed

        async def test_state_management_on_changed(self, doc_default):
            assert doc_default.is_changed is False

            doc_default.num_1 = 10

            assert doc_default.is_changed is True

    class TestHasChanged:
        async def test_state_management_off(self):
            doc = DocumentWithTurnedOffStateManagement(num_1=1, num_2=2)

            with pytest.raises(StateManagementIsTurnedOff):
                doc.has_changed

        async def test_state_management_on_not_changed(self):
            doc = DocumentWithTurnedOnStateManagement(
                num_1=1, num_2=2, internal=InternalDoc()
            )

            with pytest.raises(StateNotSaved):
                doc.has_changed

        async def test_save_previous_on_not_changed(self):
            doc = DocumentWithTurnedOnSavePrevious(
                num_1=1, num_2=2, internal=InternalDoc()
            )

            with pytest.raises(StateNotSaved):
                doc.has_changed

        async def test_save_previous_on_changed(self, doc_previous):
            assert doc_previous.has_changed is False

            doc_previous.num_1 = 10
            doc_previous._save_state()

            assert doc_previous.has_changed is True

    class TestGetChanges:
        async def test_valid(self, doc_default):
            doc_default.internal.num = 1000
            doc_default.internal.string = "new_value"
            doc_default.internal.lst.append(100)

            assert doc_default.get_changes() == {
                "internal.num": 1000,
                "internal.string": "new_value",
                "internal.lst": [1, 2, 3, 4, 5, 100],
            }

            doc_default._save_state()

            assert doc_default.get_changes() == {}

        async def test_whole(self, doc_default):
            doc_default.internal = {"num": 1000, "string": "new_value"}

            assert doc_default.get_changes() == {
                "internal.num": 1000,
                "internal.string": "new_value",
            }

        async def test_replace(self, doc_replace):
            doc_replace.internal.num = 1000
            doc_replace.internal.string = "new_value"

            assert doc_replace.get_changes() == {
                "internal": {
                    "num": 1000,
                    "string": "new_value",
                    "lst": [1, 2, 3, 4, 5],
                }
            }

        async def test_replace_whole(self, doc_replace):
            doc_replace.internal = {"num": 1000, "string": "new_value"}

            assert doc_replace.get_changes() == {
                "internal": {
                    "num": 1000,
                    "string": "new_value",
                }
            }

    class TestGetPreviousChanges:
        async def test_get_previous_changes(self, doc_previous):
            doc_previous.internal.num = 1000
            doc_previous.internal.string = "new_value"
            doc_previous.internal.lst.append(100)

            assert doc_previous.get_previous_changes() == {}

            doc_previous._save_state()

            assert doc_previous.get_previous_changes() == {
                "internal.num": 1000,
                "internal.string": "new_value",
                "internal.lst": [1, 2, 3, 4, 5, 100],
            }

    class TestRollback:
        async def test_rollback(self, doc_default, state):
            doc_default.num_1 = 100
            doc_default.rollback()

            assert doc_default.num_1 == state["num_1"]

    class TestQueries:
        async def test_save_changes(self, saved_doc_default):
            assert saved_doc_default.get_saved_state()["num_1"] == 1
            assert saved_doc_default.get_previous_saved_state() is None

            saved_doc_default.num_1 = 10000

            saved_doc_default.internal.change_private()
            assert (
                saved_doc_default.internal.get_private() == "PRIVATE_CHANGED"
            )

            await saved_doc_default.save_changes()

            assert saved_doc_default.get_saved_state()["num_1"] == 10000
            assert saved_doc_default.get_previous_saved_state() is None
            assert (
                saved_doc_default.internal.get_private() == "PRIVATE_CHANGED"
            )

            new_doc = await DocumentWithTurnedOnStateManagement.get(
                saved_doc_default.id
            )
            assert new_doc.num_1 == 10000

        async def test_save_changes_previous(self, saved_doc_previous):
            assert saved_doc_previous.get_saved_state()["num_1"] == 1
            assert saved_doc_previous.get_previous_saved_state()["num_1"] == 1

            saved_doc_previous.num_1 = 10000

            saved_doc_previous.internal.change_private()
            assert (
                saved_doc_previous.internal.get_private() == "PRIVATE_CHANGED"
            )

            await saved_doc_previous.save_changes()
            assert saved_doc_previous.get_saved_state()["num_1"] == 10000
            assert saved_doc_previous.get_previous_saved_state()["num_1"] == 1
            assert (
                saved_doc_previous.internal.get_private() == "PRIVATE_CHANGED"
            )

            new_doc = await DocumentWithTurnedOnSavePrevious.get(
                saved_doc_previous.id
            )
            assert new_doc.num_1 == 10000

        async def test_fetch_save_changes(self, house):
            data = await HouseWithRevision.all(fetch_links=True).to_list()
            house = data[0]
            window_0 = house.windows[0]
            window_0.x = 10000
            window_0.lock.k = 10000
            await window_0.save_changes()

        async def test_find_one(self, saved_doc_default, state):
            new_doc = await DocumentWithTurnedOnStateManagement.get(
                saved_doc_default.id
            )
            assert new_doc.get_saved_state() == state
            assert new_doc.get_previous_saved_state() is None

            new_doc = await DocumentWithTurnedOnStateManagement.find_one(
                DocumentWithTurnedOnStateManagement.id == saved_doc_default.id
            )
            assert new_doc.get_saved_state() == state
            assert new_doc.get_previous_saved_state() is None

        async def test_find_many(self):
            docs = []
            for i in range(10):
                docs.append(
                    DocumentWithTurnedOnStateManagement(
                        num_1=i, num_2=i + 1, internal=InternalDoc()
                    )
                )
            await DocumentWithTurnedOnStateManagement.insert_many(docs)

            found_docs = await DocumentWithTurnedOnStateManagement.find(
                DocumentWithTurnedOnStateManagement.num_1 > 4
            ).to_list()

            for doc in found_docs:
                assert doc.get_saved_state() is not None
                assert doc.get_previous_saved_state() is None

        async def test_insert(self, state_without_id):
            doc = DocumentWithTurnedOnStateManagement.parse_obj(
                state_without_id
            )
            assert doc.get_saved_state() is None
            await doc.insert()
            new_state = doc.get_saved_state()
            assert new_state["_id"] is not None
            del new_state["_id"]
            assert new_state == state_without_id

        async def test_replace(self, saved_doc_default):
            saved_doc_default.num_1 = 100
            await saved_doc_default.replace()

            assert saved_doc_default.get_saved_state()["num_1"] == 100
            assert saved_doc_default.get_previous_saved_state() is None

        async def test_replace_save_previous(self, saved_doc_previous):
            saved_doc_previous.num_1 = 100
            await saved_doc_previous.replace()

            assert saved_doc_previous.get_saved_state()["num_1"] == 100
            assert saved_doc_previous.get_previous_saved_state()["num_1"] == 1
