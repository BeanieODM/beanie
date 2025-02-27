import asyncio
from typing import Any, Dict, List, Optional

import pytest
from pydantic import BaseModel, Field

from beanie import Document, init_beanie

pytestmark = pytest.mark.asyncio


class Item(BaseModel):
    name: str
    quantity: int


class ComplexListOperationsModel(Document):
    str_list: List[str] = Field(default_factory=list)
    int_list: Optional[List[int]] = None
    nested_dict_list: List[Dict[str, Any]] = Field(default_factory=list)
    matrix: List[List[int]] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list)

    class Settings:
        name = "complex_list_operations"
        use_state_management = True


class ReplaceObjectsDocument(Document):
    int_list: List[int] = Field(default_factory=list)

    class Settings:
        name = "replace_objects_document"
        use_state_management = True
        state_management_replace_objects = True


async def test_append_operation_generates_push_with_exact_values(
    db, command_logger
):
    """Test that appending to a list generates $push operation with exact values in MongoDB"""
    await init_beanie(
        database=db, document_models=[ComplexListOperationsModel]
    )

    # Create document with initial list
    doc = ComplexListOperationsModel(
        str_list=["a", "b"],
        int_list=[1, 2],
        nested_dict_list=[{"key": "value1"}, {"key": "value2"}],
        matrix=[[1, 2], [3, 4]],
        items=[Item(name="item1", quantity=5)],
    )
    await doc.insert()

    # Clear any previous commands
    command_logger.clear()

    # Append to lists
    doc.str_list.append("c")
    doc.int_list.append(3)
    doc.nested_dict_list.append({"key": "value3"})
    doc.matrix.append([5, 6])
    doc.items.append(Item(name="item2", quantity=10))
    await doc.save_changes()

    # Check operations
    has_push = False
    push_values = {}

    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$push" in update:
            has_push = True
            push_values = update["$push"]
            break

    assert has_push, "$push operation was not found in commands"

    # Verify the exact values in the push operation
    assert "str_list" in push_values, "str_list not found in $push operation"
    assert push_values["str_list"]["$each"] == [
        "c"
    ], f"Expected push value ['c'], got {push_values['str_list']['$each']}"

    assert "int_list" in push_values, "int_list not found in $push operation"
    assert push_values["int_list"]["$each"] == [
        3
    ], f"Expected push value [3], got {push_values['int_list']['$each']}"

    # Fetch from DB and verify the values were correctly stored
    updated_doc = await ComplexListOperationsModel.get(doc.id)
    assert updated_doc.str_list == ["a", "b", "c"]
    assert updated_doc.int_list == [1, 2, 3]
    assert updated_doc.nested_dict_list == [
        {"key": "value1"},
        {"key": "value2"},
        {"key": "value3"},
    ]
    assert updated_doc.matrix == [[1, 2], [3, 4], [5, 6]]
    assert len(updated_doc.items) == 2
    assert updated_doc.items[0].name == "item1"
    assert updated_doc.items[1].name == "item2"

    await ComplexListOperationsModel.delete_all()


async def test_modify_element_updates_whole_list_with_exact_values(
    db, command_logger
):
    """Test that modifying an element in a list updates the entire list with correct values"""
    await init_beanie(
        database=db, document_models=[ComplexListOperationsModel]
    )

    # Create document with initial list
    doc = ComplexListOperationsModel(
        str_list=["a", "b", "c"],
        int_list=[1, 2, 3],
        nested_dict_list=[{"key": "value1"}, {"key": "value2"}],
        matrix=[[1, 2], [3, 4]],
        items=[
            Item(name="item1", quantity=5),
            Item(name="item2", quantity=10),
        ],
    )
    await doc.insert()

    # Clear any previous commands
    command_logger.clear()

    # Modify elements in lists
    doc.str_list[1] = "MODIFIED"
    doc.int_list[0] = 100
    doc.nested_dict_list[0]["key"] = "MODIFIED_VALUE"
    doc.matrix[1][0] = 99
    doc.items[0].quantity = 50

    await doc.save_changes()

    # Check operations
    has_set = False
    set_values = {}

    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$set" in update:
            has_set = True
            set_values = update["$set"]
            break

    assert has_set, "$set operation was not found in commands"

    # Verify the exact values in the set operations
    assert "str_list" in set_values, "str_list not found in $set operation"
    assert (
        set_values["str_list"] == ["a", "MODIFIED", "c"]
    ), f"Expected set value ['a', 'MODIFIED', 'c'], got {set_values['str_list']}"

    assert "int_list" in set_values, "int_list not found in $set operation"
    assert set_values["int_list"] == [
        100,
        2,
        3,
    ], f"Expected set value [100, 2, 3], got {set_values['int_list']}"

    # Fetch from DB and verify the values were correctly stored
    updated_doc = await ComplexListOperationsModel.get(doc.id)
    assert updated_doc.str_list == ["a", "MODIFIED", "c"]
    assert updated_doc.int_list == [100, 2, 3]
    assert updated_doc.nested_dict_list[0]["key"] == "MODIFIED_VALUE"
    assert updated_doc.matrix[1][0] == 99
    assert updated_doc.items[0].quantity == 50

    await ComplexListOperationsModel.delete_all()


async def test_multiple_list_operations_with_exact_values(db, command_logger):
    """Test handling multiple list operations in a single save_changes call with verification of exact values"""
    await init_beanie(
        database=db, document_models=[ComplexListOperationsModel]
    )

    # Create document with initial list
    doc = ComplexListOperationsModel(
        str_list=["a", "b"],
        int_list=[1, 2],
        nested_dict_list=[{"key": "value1"}],
        matrix=[[1, 2]],
        items=[Item(name="item1", quantity=5)],
    )
    await doc.insert()

    # Clear any previous commands
    command_logger.clear()

    # Multiple operations: append and modify
    doc.str_list.append("c")  # append operation
    doc.int_list[0] = 100  # modify operation
    await doc.save_changes()

    # Check operations
    has_push = False
    has_set = False
    push_values = {}
    set_values = {}

    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$push" in update:
            has_push = True
            push_values = update["$push"]
        if "$set" in update:
            has_set = True
            set_values = update["$set"]

    assert has_push, "$push operation was not found in commands"
    assert has_set, "$set operation was not found in commands"

    # Verify exact values
    assert "str_list" in push_values, "str_list not found in $push operation"
    assert push_values["str_list"]["$each"] == [
        "c"
    ], f"Expected push value ['c'], got {push_values['str_list']['$each']}"

    assert "int_list" in set_values, "int_list not found in $set operation"
    assert set_values["int_list"] == [
        100,
        2,
    ], f"Expected set value [100, 2], got {set_values['int_list']}"

    # Fetch from DB and verify
    updated_doc = await ComplexListOperationsModel.get(doc.id)
    assert updated_doc.str_list == ["a", "b", "c"]
    assert updated_doc.int_list == [100, 2]

    await ComplexListOperationsModel.delete_all()


async def test_nested_list_updates_use_full_update(db, command_logger):
    """Test that updating lists nested in lists will always generate a full update of the outer list"""
    await init_beanie(
        database=db, document_models=[ComplexListOperationsModel]
    )

    # Create document with initial nested lists
    doc = ComplexListOperationsModel(
        str_list=[],
        int_list=[],
        nested_dict_list=[{"key": "value1", "nested_list": [1, 2, 3]}],
        matrix=[[1, 2], [3, 4], [5, 6]],
        items=[],
    )
    await doc.insert()

    # Clear any previous commands
    command_logger.clear()

    # Modify a nested list element
    doc.matrix[1][0] = 99  # Modify element in nested list
    await doc.save_changes()

    # Check operations
    has_set_on_outer_list = False
    set_values = {}

    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$set" in update and "matrix" in update["$set"]:
            has_set_on_outer_list = True
            set_values = update["$set"]
            break

    assert has_set_on_outer_list, "Full update on the outer list was not found"
    assert "matrix" in set_values, "Matrix not found in $set operation"

    # Verify the entire matrix was updated, not just the nested element
    assert set_values["matrix"] == [
        [1, 2],
        [99, 4],
        [5, 6],
    ], f"Expected set value for matrix, got {set_values['matrix']}"

    # Now test updating a list in a nested dictionary
    command_logger.clear()  # Clear previous commands

    doc.nested_dict_list[0]["nested_list"].append(
        4
    )  # Append to a list inside a dictionary
    await doc.save_changes()

    # Verify that the entire outer list (nested_dict_list) was updated
    has_set_on_outer_dict_list = False
    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$set" in update and "nested_dict_list" in update["$set"]:
            has_set_on_outer_dict_list = True
            set_values = update["$set"]
            break

    assert (
        has_set_on_outer_dict_list
    ), "Full update on the nested_dict_list was not found"
    assert set_values["nested_dict_list"][0]["nested_list"] == [
        1,
        2,
        3,
        4,
    ], "Nested list not updated correctly"

    # Fetch from DB and verify the values
    updated_doc = await ComplexListOperationsModel.get(doc.id)
    assert updated_doc.matrix == [[1, 2], [99, 4], [5, 6]]
    assert updated_doc.nested_dict_list[0]["nested_list"] == [1, 2, 3, 4]

    await ComplexListOperationsModel.delete_all()


async def test_concurrent_updates_to_list(db):
    """Test that concurrent updates to lists are correctly saved"""

    await init_beanie(
        database=db, document_models=[ComplexListOperationsModel]
    )

    # Create initial document with empty lists
    doc = ComplexListOperationsModel(str_list=[], int_list=[])
    await doc.insert()
    doc_id = doc.id

    # Define concurrent update functions
    async def append_to_str_list():
        doc1 = await ComplexListOperationsModel.get(doc_id)
        doc1.str_list.append("concurrent1")
        await doc1.save_changes()

    async def append_to_int_list():
        doc2 = await ComplexListOperationsModel.get(doc_id)
        doc2.int_list.append(42)
        await doc2.save_changes()

    async def update_both_lists():
        doc3 = await ComplexListOperationsModel.get(doc_id)
        doc3.str_list.append("concurrent2")
        doc3.int_list.append(99)
        await doc3.save_changes()

    # Execute concurrent updates
    await asyncio.gather(
        append_to_str_list(), append_to_int_list(), update_both_lists()
    )

    # Verify final state reflects all updates
    final_doc = await ComplexListOperationsModel.get(doc_id)
    assert (
        "concurrent1" in final_doc.str_list
    ), "First concurrent str_list update missing"
    assert (
        "concurrent2" in final_doc.str_list
    ), "Second concurrent str_list update missing"
    assert 42 in final_doc.int_list, "First concurrent int_list update missing"
    assert (
        99 in final_doc.int_list
    ), "Second concurrent int_list update missing"

    # All items should be preserved with no duplicates
    assert (
        len(final_doc.str_list) == 2
    ), "str_list contains wrong number of items"
    assert (
        len(final_doc.int_list) == 2
    ), "int_list contains wrong number of items"

    await ComplexListOperationsModel.delete_all()


async def test_state_management_replace_objects_behavior(db, command_logger):
    """Test that when state_management_replace_objects is True, lists are always fully updated"""
    await init_beanie(database=db, document_models=[ReplaceObjectsDocument])

    # Create document with initial list
    doc = ReplaceObjectsDocument(int_list=[1, 2, 3])
    await doc.insert()

    # Clear any previous commands
    command_logger.clear()

    # Append to the list (which would normally use $push if replace_objects were False)
    doc.int_list.append(4)
    await doc.save_changes()

    # Check operations - should use $set even for append operations
    has_push = False
    has_set = False
    set_values = {}

    for cmd_name, command in command_logger.get_commands_by_name(
        "findAndModify"
    ):
        update = command["update"]
        if "$push" in update:
            has_push = True
        if "$set" in update and "int_list" in update["$set"]:
            has_set = True
            set_values = update["$set"]
            break

    # With replace_objects=True, we should always use $set, not $push
    assert not has_push, "$push operation was found but shouldn't be used with state_management_replace_objects=True"
    assert has_set, "$set operation for int_list was not found"
    assert set_values["int_list"] == [
        1,
        2,
        3,
        4,
    ], f"Expected set value [1, 2, 3, 4], got {set_values['int_list']}"

    # Verify final state
    final_doc = await ReplaceObjectsDocument.get(doc.id)
    assert final_doc.int_list == [1, 2, 3, 4]

    await ReplaceObjectsDocument.delete_all()
