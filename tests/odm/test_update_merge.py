"""Tests for beanie.odm.utils.update_merge module.

Unit tests for the update expression merger. These do not require a
database and verify the merge logic in isolation.
"""

import pytest

from beanie.odm.operators.update.general import (
    Inc,
    Set,
    SetRevisionId,
    Unset,
)
from beanie.odm.utils.update_merge import (
    ActionConflictResolution,
    MergeConflictError,
    _consolidate_update_query,
    _extract_targeted_fields,
    merge_update_expressions,
)


class TestConsolidateUpdateQuery:
    """Tests for _consolidate_update_query."""

    def test_empty_args(self):
        result = _consolidate_update_query([])
        assert result == {}

    def test_single_dict_set(self):
        result = _consolidate_update_query([{"$set": {"name": "bob"}}])
        assert result == {"$set": {"name": "bob"}}

    def test_single_set_operator(self):
        result = _consolidate_update_query([Set({"name": "bob"})])
        assert result == {"$set": {"name": "bob"}}

    def test_multiple_set_operators_merged(self):
        result = _consolidate_update_query(
            [Set({"name": "bob"}), Set({"age": 30})]
        )
        assert result == {"$set": {"name": "bob", "age": 30}}

    def test_mixed_operators(self):
        result = _consolidate_update_query(
            [Set({"name": "bob"}), Inc({"counter": 1})]
        )
        assert result == {"$set": {"name": "bob"}, "$inc": {"counter": 1}}

    def test_set_revision_id_skipped(self):
        from uuid import uuid4

        rev = SetRevisionId(uuid4())
        result = _consolidate_update_query([Set({"name": "bob"}), rev])
        assert result == {"$set": {"name": "bob"}}

    def test_list_pipeline_skipped(self):
        result = _consolidate_update_query(
            [Set({"name": "bob"}), [{"$addFields": {"x": 1}}]]
        )
        assert result == {"$set": {"name": "bob"}}

    def test_dict_and_operator_merged(self):
        result = _consolidate_update_query(
            [{"$set": {"name": "bob"}}, Set({"age": 30})]
        )
        assert result == {"$set": {"name": "bob", "age": 30}}

    def test_overlapping_set_last_wins(self):
        result = _consolidate_update_query(
            [Set({"name": "bob"}), Set({"name": "alice"})]
        )
        assert result == {"$set": {"name": "alice"}}

    def test_unset_operator(self):
        result = _consolidate_update_query(
            [Set({"name": "bob"}), Unset({"old_field": ""})]
        )
        assert result == {
            "$set": {"name": "bob"},
            "$unset": {"old_field": ""},
        }


class TestExtractTargetedFields:
    """Tests for _extract_targeted_fields."""

    def test_empty(self):
        assert _extract_targeted_fields({}) == set()

    def test_single_operator(self):
        consolidated = {"$set": {"name": "bob", "age": 30}}
        assert _extract_targeted_fields(consolidated) == {"name", "age"}

    def test_multiple_operators(self):
        consolidated = {
            "$set": {"name": "bob"},
            "$inc": {"counter": 1},
            "$unset": {"old": ""},
        }
        assert _extract_targeted_fields(consolidated) == {
            "name",
            "counter",
            "old",
        }


class TestMergeUpdateExpressions:
    """Tests for merge_update_expressions -- the main merge function."""

    # -- No action changes --

    def test_no_action_changes_returns_copy(self):
        args = [Set({"name": "bob"})]
        result = merge_update_expressions(args, {})
        assert len(result) == 1

    # -- UPDATE_WINS (default) --

    def test_update_wins_no_conflict(self):
        args = [{"$set": {"name": "bob"}}]
        changes = {"tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$set"]["tag"] == "updated"

    def test_update_wins_conflict_keeps_update(self):
        args = [{"$set": {"name": "bob", "tag": "explicit"}}]
        changes = {"tag": "from_action", "extra": "value"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$set"]["tag"] == "explicit"
        assert result[0]["$set"]["extra"] == "value"

    def test_update_wins_conflict_with_inc(self):
        args = [Inc({"counter": 1})]
        changes = {"counter": 42, "tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$inc"]["counter"] == 1
        assert result[0]["$set"]["tag"] == "updated"
        assert "counter" not in result[0].get("$set", {})

    def test_update_wins_with_set_operator(self):
        args = [Set({"name": "bob"})]
        changes = {"tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$set"]["tag"] == "updated"

    # -- ACTION_WINS --

    def test_action_wins_no_conflict(self):
        args = [{"$set": {"name": "bob"}}]
        changes = {"tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.ACTION_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$set"]["tag"] == "updated"

    def test_action_wins_conflict_action_takes_precedence(self):
        args = [{"$set": {"name": "bob", "tag": "explicit"}}]
        changes = {"tag": "from_action"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.ACTION_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$set"]["tag"] == "from_action"

    def test_action_wins_removes_conflicting_non_set_operators(self):
        args = [Inc({"counter": 1}), Set({"name": "bob"})]
        changes = {"counter": 42}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.ACTION_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["counter"] == 42
        assert result[0]["$set"]["name"] == "bob"
        assert "$inc" not in result[0]

    # -- ACTION_OVERRIDE --

    def test_action_override_replaces_everything(self):
        args = [Set({"name": "bob"}), Inc({"counter": 1})]
        changes = {"tag": "overridden"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.ACTION_OVERRIDE
        )
        assert len(result) == 1
        assert result[0] == {"$set": {"tag": "overridden"}}

    def test_action_override_preserves_set_revision_id(self):
        from uuid import uuid4

        rev = SetRevisionId(uuid4())
        args = [Set({"name": "bob"}), rev]
        changes = {"tag": "overridden"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.ACTION_OVERRIDE
        )
        assert len(result) == 2
        assert result[0] == {"$set": {"tag": "overridden"}}
        assert isinstance(result[1], SetRevisionId)

    # -- RAISE --

    def test_raise_no_conflict(self):
        args = [{"$set": {"name": "bob"}}]
        changes = {"tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.RAISE
        )
        assert len(result) == 1
        assert result[0]["$set"]["tag"] == "updated"

    def test_raise_with_conflict(self):
        args = [{"$set": {"name": "bob"}}]
        changes = {"name": "from_action"}
        with pytest.raises(MergeConflictError) as exc_info:
            merge_update_expressions(
                args, changes, ActionConflictResolution.RAISE
            )
        assert "name" in exc_info.value.conflicting_fields

    def test_raise_conflict_with_inc(self):
        args = [Inc({"counter": 1})]
        changes = {"counter": 42}
        with pytest.raises(MergeConflictError) as exc_info:
            merge_update_expressions(
                args, changes, ActionConflictResolution.RAISE
            )
        assert "counter" in exc_info.value.conflicting_fields

    # -- Edge cases --

    def test_empty_update_args_with_changes(self):
        result = merge_update_expressions(
            [], {"tag": "new"}, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["tag"] == "new"

    def test_multiple_operators_no_conflict(self):
        args = [
            Set({"name": "bob"}),
            Inc({"counter": 1}),
            Unset({"old_field": ""}),
        ]
        changes = {"tag": "updated"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert len(result) == 1
        assert result[0]["$set"]["tag"] == "updated"
        assert result[0]["$set"]["name"] == "bob"
        assert result[0]["$inc"]["counter"] == 1
        assert result[0]["$unset"]["old_field"] == ""

    def test_dotted_field_paths(self):
        args = [Set({"nested.field": "value"})]
        changes = {"nested.field": "from_action", "other": "ok"}
        result = merge_update_expressions(
            args, changes, ActionConflictResolution.UPDATE_WINS
        )
        assert result[0]["$set"]["nested.field"] == "value"
        assert result[0]["$set"]["other"] == "ok"

    def test_default_strategy_is_update_wins(self):
        args = [{"$set": {"name": "bob", "tag": "explicit"}}]
        changes = {"tag": "from_action", "extra": "value"}
        result = merge_update_expressions(args, changes)
        assert result[0]["$set"]["tag"] == "explicit"
        assert result[0]["$set"]["extra"] == "value"
