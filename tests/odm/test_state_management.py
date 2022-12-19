import pytest
from bson import ObjectId

from beanie import PydanticObjectId, WriteRules
from beanie.exceptions import StateManagementIsTurnedOff, StateNotSaved
from tests.odm.models import (
    DocumentWithTurnedOffStateManagement,
    DocumentWithTurnedOnReplaceObjects,
    DocumentWithTurnedOnStateManagement,
    HouseWithRevision,
    InternalDoc,
    LockWithRevision,
    WindowWithRevision,
    StateAndDecimalFieldModel,
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
    return DocumentWithTurnedOnStateManagement.parse_obj(state)


@pytest.fixture
def doc_replace(state):
    return DocumentWithTurnedOnReplaceObjects.parse_obj(state)


@pytest.fixture
async def saved_doc_default(doc_default):
    await doc_default.insert()
    return doc_default


def test_use_state_management_property():
    assert DocumentWithTurnedOnStateManagement.use_state_management() is True
    assert DocumentWithTurnedOffStateManagement.use_state_management() is False


def test_save_state():
    doc = DocumentWithTurnedOnStateManagement(
        num_1=1, num_2=2, internal=InternalDoc(num=1, string="s")
    )
    assert doc.get_saved_state() is None
    doc.id = PydanticObjectId()
    doc._save_state()
    assert doc.get_saved_state() == {
        "num_1": 1,
        "num_2": 2,
        "internal": {"num": 1, "string": "s", "lst": [1, 2, 3, 4, 5]},
        "_id": doc.id,
    }


def test_parse_object_with_saving_state():
    obj = {
        "num_1": 1,
        "num_2": 2,
        "_id": ObjectId(),
        "internal": InternalDoc(),
    }
    doc = DocumentWithTurnedOnStateManagement.parse_obj(obj)
    assert doc.get_saved_state() == obj


def test_saved_state_needed():
    doc_1 = DocumentWithTurnedOffStateManagement(num_1=1, num_2=2)
    with pytest.raises(StateManagementIsTurnedOff):
        doc_1.is_changed

    doc_2 = DocumentWithTurnedOnStateManagement(
        num_1=1, num_2=2, internal=InternalDoc()
    )
    with pytest.raises(StateNotSaved):
        doc_2.is_changed


def test_if_changed(doc_default):
    assert doc_default.is_changed is False
    doc_default.num_1 = 10
    assert doc_default.is_changed is True


def test_get_changes_default(doc_default):
    doc_default.internal.num = 1000
    doc_default.internal.string = "new_value"
    doc_default.internal.lst.append(100)
    assert doc_default.get_changes() == {
        "internal.num": 1000,
        "internal.string": "new_value",
        "internal.lst": [1, 2, 3, 4, 5, 100],
    }


def test_get_changes_default_whole(doc_default):
    doc_default.internal = {"num": 1000, "string": "new_value"}
    assert doc_default.get_changes() == {
        "internal.num": 1000,
        "internal.string": "new_value",
    }


def test_get_changes_replace(doc_replace):
    doc_replace.internal.num = 1000
    doc_replace.internal.string = "new_value"
    assert doc_replace.get_changes() == {
        "internal": {
            "num": 1000,
            "string": "new_value",
            "lst": [1, 2, 3, 4, 5],
        }
    }


def test_get_changes_replace_whole(doc_replace):
    doc_replace.internal = {"num": 1000, "string": "new_value"}
    assert doc_replace.get_changes() == {
        "internal": {
            "num": 1000,
            "string": "new_value",
        }
    }


async def test_save_changes(saved_doc_default):
    saved_doc_default.internal.num = 10000
    saved_doc_default.internal.change_private()
    assert saved_doc_default.internal.get_private() == "PRIVATE_CHANGED"

    await saved_doc_default.save_changes()
    assert saved_doc_default.get_saved_state()["internal"]["num"] == 10000
    assert saved_doc_default.internal.get_private() == "PRIVATE_CHANGED"

    new_doc = await DocumentWithTurnedOnStateManagement.get(
        saved_doc_default.id
    )
    assert new_doc.internal.num == 10000


async def test_find_one(saved_doc_default, state):
    new_doc = await DocumentWithTurnedOnStateManagement.get(
        saved_doc_default.id
    )
    assert new_doc.get_saved_state() == state

    new_doc = await DocumentWithTurnedOnStateManagement.find_one(
        DocumentWithTurnedOnStateManagement.id == saved_doc_default.id
    )
    assert new_doc.get_saved_state() == state


async def test_find_many():
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


async def test_insert(state_without_id):
    doc = DocumentWithTurnedOnStateManagement.parse_obj(state_without_id)
    assert doc.get_saved_state() is None
    await doc.insert()
    new_state = doc.get_saved_state()
    assert new_state["_id"] is not None
    del new_state["_id"]
    assert new_state == state_without_id


async def test_replace(saved_doc_default):
    saved_doc_default.num_1 = 100
    await saved_doc_default.replace()
    assert saved_doc_default.get_saved_state()["num_1"] == 100


async def test_save_chages(saved_doc_default):
    saved_doc_default.num_1 = 100
    await saved_doc_default.save_changes()
    assert saved_doc_default.get_saved_state()["num_1"] == 100


async def test_rollback(doc_default, state):
    doc_default.num_1 = 100
    doc_default.rollback()
    assert doc_default.num_1 == state["num_1"]


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


async def test_fetch_save_changes(house):
    data = await HouseWithRevision.all(fetch_links=True).to_list()
    house = data[0]
    window_0 = house.windows[0]
    window_0.x = 10000
    window_0.lock.k = 10000
    await window_0.save_changes()


async def test_state_with_decimal_field():
    await StateAndDecimalFieldModel(amt=10.01).insert()
    await StateAndDecimalFieldModel.all().to_list()
