import pytest

from beanie import Before, After

from tests.sync.models import (
    DocumentWithActions,
    InheritedDocumentWithActions,
    DocumentWithActions2,
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
    def test_actions_insert(self, doc_class):
        test_name = f"test_actions_insert_{doc_class}"
        sample = doc_class(name=test_name)

        sample.insert()
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
    def test_actions_replace(self, doc_class):
        test_name = f"test_actions_replace_{doc_class}"
        sample = doc_class(name=test_name)

        sample.insert()

        sample.replace()
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
    def test_skip_actions_insert(self, doc_class):
        test_name = f"test_skip_actions_insert_{doc_class}"
        sample = doc_class(name=test_name)

        sample.insert(skip_actions=[After, "capitalize_name"])
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
    def test_skip_actions_replace(self, doc_class):
        test_name = f"test_skip_actions_replace{doc_class}"
        sample = doc_class(name=test_name)

        sample.insert()

        sample.replace(skip_actions=[Before, "num_3_change"])
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
    def test_actions_delete(self, doc_class):
        test_name = f"test_actions_delete_{doc_class}"
        sample = doc_class(name=test_name)

        sample.delete()
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
    def test_actions_update(self, doc_class):
        test_name = f"test_actions_update_{doc_class}"
        sample = doc_class(name=test_name)
        sample.save()

        sample.update({"$set": {"name": "new_name"}})
        assert sample.name == "new_name"
        assert sample.num_1 == 2
        assert sample.num_2 == 9

        sample.set({"name": "awesome_name"}, skip_sync=True)

        assert sample.num_1 == 3
        assert sample.num_2 == 8

        sample._sync()
        assert sample.name == "awesome_name"
