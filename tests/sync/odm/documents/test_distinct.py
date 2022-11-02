from tests.sync.models import DocumentTestModel


def test_distinct_unique(documents, document_not_inserted):
    documents(1, "uno")
    documents(2, "dos")
    documents(3, "cuatro")
    expected_result = ["cuatro", "dos", "uno"]
    unique_test_strs = DocumentTestModel.distinct("test_str", {})
    assert unique_test_strs == expected_result
    document_not_inserted.test_str = "uno"
    document_not_inserted.insert()
    another_unique_test_strs = DocumentTestModel.distinct("test_str", {})
    assert another_unique_test_strs == expected_result


def test_distinct_different_value(documents, document_not_inserted):
    documents(1, "uno")
    documents(2, "dos")
    documents(3, "cuatro")
    expected_result = ["cuatro", "dos", "uno"]
    unique_test_strs = DocumentTestModel.distinct("test_str", {})
    assert unique_test_strs == expected_result
    document_not_inserted.test_str = "diff_val"
    document_not_inserted.insert()
    another_unique_test_strs = DocumentTestModel.distinct("test_str", {})
    assert not another_unique_test_strs == expected_result
    assert another_unique_test_strs == ["cuatro", "diff_val", "dos", "uno"]
