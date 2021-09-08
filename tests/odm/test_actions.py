from tests.odm.models import DocumentWithActions


async def test_actions_insert_replace():
    test_name = "test_name"
    sample = DocumentWithActions(name=test_name)

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
