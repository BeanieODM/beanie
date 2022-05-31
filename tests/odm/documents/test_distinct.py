from tests.odm.models import DocumentTestModel


async def test_distinct_unique(documents, document_not_inserted):
    await documents(1, "uno")
    await documents(2, "dos")
    await documents(3, "cuatro")
    expected_result = ["cuatro", "dos", "uno"]
    unique_test_strs = await DocumentTestModel.distinct("test_str", {})
    assert unique_test_strs == expected_result
    document_not_inserted.test_str = "uno"
    await document_not_inserted.insert()
    another_unique_test_strs = await DocumentTestModel.distinct("test_str", {})
    assert another_unique_test_strs == expected_result


async def test_distinct_different_value(documents, document_not_inserted):
    await documents(1, "uno")
    await documents(2, "dos")
    await documents(3, "cuatro")
    expected_result = ["cuatro", "dos", "uno"]
    unique_test_strs = await DocumentTestModel.distinct("test_str", {})
    assert unique_test_strs == expected_result
    document_not_inserted.test_str = "diff_val"
    await document_not_inserted.insert()
    another_unique_test_strs = await DocumentTestModel.distinct("test_str", {})
    assert not another_unique_test_strs == expected_result
    assert another_unique_test_strs == ["cuatro", "diff_val", "dos", "uno"]
