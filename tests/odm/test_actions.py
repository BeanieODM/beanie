import pytest

from beanie import After, Before
from tests.odm.models import (
    DocumentWithActions,
    DocumentWithActions2,
    DocumentWithActionWinsStrategy,
    DocumentWithUpdateFieldAction,
    DocumentWithValidateOnSaveAction,
    InheritedDocumentWithActions,
)


class TestActions:
    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_actions_insert(self, doc_class):
        test_name = f"test_actions_insert_{doc_class}"
        sample = doc_class(name=test_name)

        await sample.insert()
        assert sample.name != test_name
        assert sample.name == test_name.capitalize()
        assert sample.num_1 == 1
        assert sample.num_2 == 9

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_actions_replace(self, doc_class):
        test_name = f"test_actions_replace_{doc_class}"
        sample = doc_class(name=test_name)

        await sample.insert()

        await sample.replace()
        assert sample.num_1 == 2
        assert sample.num_3 == 99

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_skip_actions_insert(self, doc_class):
        test_name = f"test_skip_actions_insert_{doc_class}"
        sample = doc_class(name=test_name)

        await sample.insert(skip_actions=[After, "capitalize_name"])
        # capitalize_name has been skipped
        assert sample.name == test_name
        # add_one has not been skipped
        assert sample.num_1 == 1
        # num_2_change has been skipped
        assert sample.num_2 == 10

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_skip_actions_replace(self, doc_class):
        test_name = f"test_skip_actions_replace{doc_class}"
        sample = doc_class(name=test_name)

        await sample.insert()

        await sample.replace(skip_actions=[Before, "num_3_change"])
        # add_one has been skipped
        assert sample.num_1 == 1
        # num_3_change has been skipped
        assert sample.num_3 == 100

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_actions_delete(self, doc_class):
        test_name = f"test_actions_delete_{doc_class}"
        sample = doc_class(name=test_name)

        await sample.delete()
        assert sample.Inner.inner_num_1 == 1
        assert sample.Inner.inner_num_2 == 2

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_actions_update(self, doc_class):
        test_name = f"test_actions_update_{doc_class}"
        sample = doc_class(name=test_name)
        await sample.insert()

        await sample.update({"$set": {"name": "new_name"}})
        assert sample.name == "new_name"
        assert sample.num_1 == 1
        assert sample.num_2 == 9
        assert sample._private_num == 101

        await sample.set({"name": "awesome_name"})

        assert sample._private_num == 102
        assert sample.num_2 == 9
        assert sample.name == "awesome_name"

    @pytest.mark.parametrize(
        "doc_class",
        [
            DocumentWithActions,
            DocumentWithActions2,
            InheritedDocumentWithActions,
        ],
    )
    async def test_actions_save(self, doc_class):
        test_name = f"test_actions_save_{doc_class}"
        sample = doc_class(name=test_name)
        await sample.save()
        assert sample.num_1 == 1


class TestBeforeEventUpdatePersistence:
    """Tests for #1103: before_event(Update) changes must be persisted to DB."""

    async def test_update_persists_before_event_changes(self):
        doc = DocumentWithUpdateFieldAction(name="alice")
        await doc.insert()

        await doc.update({"$set": {"name": "bob"}})
        assert doc.name == "bob"
        assert doc.tag == "updated"

        refetched = await DocumentWithUpdateFieldAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.tag == "updated"
        assert refetched.name == "bob"

    async def test_set_persists_before_event_changes(self):
        doc = DocumentWithUpdateFieldAction(name="alice")
        await doc.insert()

        await doc.set({"name": "charlie"})
        assert doc.tag == "updated"

        refetched = await DocumentWithUpdateFieldAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.tag == "updated"
        assert refetched.name == "charlie"

    async def test_update_skip_actions_before(self):
        doc = DocumentWithUpdateFieldAction(name="alice")
        await doc.insert()

        await doc.update({"$set": {"name": "bob"}}, skip_actions=[Before])

        refetched = await DocumentWithUpdateFieldAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.tag is None
        assert refetched.name == "bob"


class TestValidateOnSaveWithBeforeEvent:
    """Tests for #894: before_event must run after validate_on_save."""

    async def test_insert_before_event_survives_validation(self):
        doc = DocumentWithValidateOnSaveAction(name="  Hello World  ")
        await doc.insert()

        assert doc.normalized_name == "hello world"

        refetched = await DocumentWithValidateOnSaveAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.normalized_name == "hello world"

    async def test_save_before_event_survives_validation(self):
        doc = DocumentWithValidateOnSaveAction(name="initial")
        await doc.insert()

        doc.name = "  Updated Name  "
        await doc.save()

        assert doc.normalized_name == "updated name"

        refetched = await DocumentWithValidateOnSaveAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.normalized_name == "updated name"

    async def test_replace_before_event_survives_validation(self):
        doc = DocumentWithValidateOnSaveAction(name="initial")
        await doc.insert()

        doc.name = "  Replaced Name  "
        await doc.replace()

        assert doc.normalized_name == "replaced name"

        refetched = await DocumentWithValidateOnSaveAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.normalized_name == "replaced name"


class TestActionConflictResolutionIntegration:
    """Integration tests for action_conflict_resolution setting with real DB."""

    async def test_action_wins_overrides_explicit_set(self):
        doc = DocumentWithActionWinsStrategy(name="alice")
        await doc.insert()

        await doc.update({"$set": {"name": "bob", "tag": "explicit"}})

        refetched = await DocumentWithActionWinsStrategy.find_one(
            {"_id": doc.id}
        )
        assert refetched.name == "bob"
        assert refetched.tag == "action_value"

    async def test_action_wins_via_set_method(self):
        doc = DocumentWithActionWinsStrategy(name="alice")
        await doc.insert()

        await doc.set({"tag": "explicit"})

        refetched = await DocumentWithActionWinsStrategy.find_one(
            {"_id": doc.id}
        )
        assert refetched.tag == "action_value"

    async def test_update_wins_non_conflicting_fields_persisted(self):
        doc = DocumentWithUpdateFieldAction(name="alice")
        await doc.insert()

        await doc.update({"$set": {"name": "bob"}})

        refetched = await DocumentWithUpdateFieldAction.find_one(
            {"_id": doc.id}
        )
        assert refetched.name == "bob"
        assert refetched.tag == "updated"
