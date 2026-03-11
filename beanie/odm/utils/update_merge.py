"""Update expression merging for before_event action changes.

When a ``before_event(Update)`` handler modifies document fields, those
changes must be included in the update expression sent to MongoDB. This
module provides a general-purpose merger with configurable conflict
resolution.

A *conflict* occurs when a field (identified by its dotted path in the
MongoDB document) is modified by both the explicit update arguments and
a ``before_event`` handler.

Strategies
----------
``UPDATE_WINS`` (default)
    Explicit update arguments take precedence. Action changes are
    included only for fields not already targeted by the update.

``ACTION_WINS``
    Action changes take precedence. For conflicting fields, the
    before_event value replaces whatever the update expression would
    have set. Non-conflicting update fields are preserved.

``ACTION_OVERRIDE``
    Action changes completely replace the entire update expression.
    The original update arguments are discarded.

``RAISE``
    Raises ``MergeConflictError`` if any field is modified by both
    the update expression and a before_event handler.
"""

from enum import Enum
from typing import Any, Dict, List, Mapping, Set, Union

from beanie.odm.operators.update import BaseUpdateOperator
from beanie.odm.operators.update.general import SetRevisionId


class ActionConflictResolution(str, Enum):
    """Strategy for resolving conflicts between before_event field changes
    and explicit update arguments.
    """

    UPDATE_WINS = "update_wins"
    ACTION_WINS = "action_wins"
    ACTION_OVERRIDE = "action_override"
    RAISE = "raise"


class MergeConflictError(Exception):
    """Raised when ``RAISE`` strategy detects conflicting fields."""

    def __init__(self, conflicting_fields: Set[str]) -> None:
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(sorted(conflicting_fields))
        super().__init__(
            f"before_event and update expression both modify: {fields_str}. "
            f"Use a different ActionConflictResolution strategy or adjust "
            f"the before_event handler."
        )


def _consolidate_update_query(
    update_args: List[Union[Dict[str, Any], Mapping[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Build a single consolidated MongoDB update dict from a list of
    update expressions.

    Merges multiple ``$set``, ``$inc``, ``$unset``, etc. into one dict
    where each operator key maps to a combined dict of field-value pairs.

    ``SetRevisionId`` and aggregation pipeline (list) expressions are
    skipped -- they are handled separately by the query builder.

    :param update_args: list of update expressions (dicts,
        BaseUpdateOperator instances, etc.)
    :return: consolidated ``{operator: {field: value, ...}, ...}`` dict
    """
    consolidated: Dict[str, Dict[str, Any]] = {}

    for arg in update_args:
        if isinstance(arg, SetRevisionId):
            continue
        if isinstance(arg, list):
            continue

        if isinstance(arg, BaseUpdateOperator):
            raw = dict(arg.query)
        elif isinstance(arg, dict):
            raw = arg
        elif isinstance(arg, Mapping):
            raw = dict(arg)
        else:
            continue

        for operator_key, fields in raw.items():
            if not isinstance(fields, (dict, Mapping)):
                continue
            if operator_key not in consolidated:
                consolidated[operator_key] = {}
            consolidated[operator_key].update(fields)

    return consolidated


def _extract_targeted_fields(
    consolidated: Dict[str, Dict[str, Any]],
) -> Set[str]:
    """Extract the set of all field names targeted by any update operator.

    :param consolidated: output of ``_consolidate_update_query``
    :return: set of dotted field paths
    """
    fields: Set[str] = set()
    for operator_fields in consolidated.values():
        fields.update(operator_fields.keys())
    return fields


def merge_update_expressions(
    update_args: List[Union[Dict[str, Any], Mapping[str, Any]]],
    action_changes: Dict[str, Any],
    strategy: ActionConflictResolution = ActionConflictResolution.UPDATE_WINS,
) -> List[Union[Dict[str, Any], Mapping[str, Any]]]:
    """Merge before_event field changes into update arguments.

    Produces a single consolidated update expression that includes both
    the original update arguments and the before_event changes, resolved
    according to the chosen conflict strategy.

    Expressions that are not standard update operators (``SetRevisionId``,
    aggregation pipelines) are preserved and passed through unchanged.

    :param update_args: original update expressions passed to
        ``Document.update()``
    :param action_changes: dict of ``{field: value}`` changes produced
        by before_event handlers
    :param strategy: conflict resolution strategy
    :return: new list of update expressions with action changes merged
    :raises MergeConflictError: when strategy is ``RAISE`` and conflicts
        exist
    """
    if not action_changes:
        return list(update_args)

    if strategy == ActionConflictResolution.ACTION_OVERRIDE:
        passthrough = _collect_passthrough(update_args)
        return [{"$set": dict(action_changes)}] + passthrough

    consolidated = _consolidate_update_query(update_args)
    targeted = _extract_targeted_fields(consolidated)
    conflicting = set(action_changes.keys()) & targeted

    if conflicting and strategy == ActionConflictResolution.RAISE:
        raise MergeConflictError(conflicting)

    set_fields = consolidated.get("$set", {})

    if strategy in (
        ActionConflictResolution.UPDATE_WINS,
        ActionConflictResolution.RAISE,
    ):
        for key, value in action_changes.items():
            if key not in targeted:
                set_fields[key] = value

    elif strategy == ActionConflictResolution.ACTION_WINS:
        # Remove conflicting fields from non-$set operators
        for operator_key in list(consolidated.keys()):
            if operator_key == "$set":
                continue
            for field in conflicting:
                consolidated[operator_key].pop(field, None)
            if not consolidated[operator_key]:
                del consolidated[operator_key]

        set_fields.update(action_changes)

    if set_fields:
        consolidated["$set"] = set_fields

    # Remove empty operators
    consolidated = {k: v for k, v in consolidated.items() if v}

    passthrough = _collect_passthrough(update_args)

    if consolidated:
        return [consolidated] + passthrough
    return passthrough if passthrough else list(update_args)


def _collect_passthrough(
    update_args: List[Union[Dict[str, Any], Mapping[str, Any]]],
) -> List[Any]:
    """Collect expressions that the merger does not process.

    ``SetRevisionId`` and aggregation pipeline (list) expressions are
    managed elsewhere and must be passed through unchanged.

    :param update_args: original update expression list
    :return: list of pass-through expressions
    """
    result: List[Any] = []
    for arg in update_args:
        if isinstance(arg, SetRevisionId):
            result.append(arg)
        elif isinstance(arg, list):
            result.append(arg)
    return result
