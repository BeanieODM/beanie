import pytest

from tests.odm.models import DocumentWithActions, InheritedDocumentWithActions


@pytest.mark.parametrize(
    "doc_class", [DocumentWithActions, InheritedDocumentWithActions]
)
async def test_actions_insert_replace(doc_class):
    test_name = "test_name"
    sample = doc_class(name=test_name)

    # TEST INSERT
    await sample.insert()
    assert sample.name != test_name
    assert sample.name == test_name.capitalize()
    assert sample.num_1 == 1
    assert sample.num_2 == 9

    # TEST REPLACE
    await sample.replace()
    assert sample.num_1 == 2
    assert sample.num_3 == 99
