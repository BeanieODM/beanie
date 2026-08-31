"""Standalone test for the bool type compliance fix (issue #1000).
Does NOT require MongoDB - tests only the query property output.
Run with: python -m pytest test_bool_fix_standalone.py -v
"""

import sys

sys.path.insert(0, "/c/Users/kbula/beanie-fix")

from collections.abc import Mapping

import pytest

from beanie.odm.operators.find.logical import And, Nor, Or


class TestBoolTypeCompliance:
    """Tests for issue #1000: Logical operators should handle bool expressions."""

    def test_or_with_true(self):
        """Or(True) should return a Mapping, not a bare bool."""
        q = Or(True).query
        assert q == {"$or": [True]}
        assert isinstance(q, Mapping)

    def test_or_with_false(self):
        """Or(False) should return a Mapping, not a bare bool."""
        q = Or(False).query
        assert q == {"$or": [False]}
        assert isinstance(q, Mapping)

    def test_and_with_true(self):
        """And(True) should return a Mapping, not a bare bool."""
        q = And(True).query
        assert q == {"$and": [True]}
        assert isinstance(q, Mapping)

    def test_and_with_false(self):
        """And(False) should return a Mapping, not a bare bool."""
        q = And(False).query
        assert q == {"$and": [False]}
        assert isinstance(q, Mapping)

    def test_or_with_multiple_bool_expressions(self):
        """Or(True, False) should wrap in $or list."""
        q = Or(True, False).query
        assert q == {"$or": [True, False]}

    def test_and_with_multiple_bool_expressions(self):
        """And(True, False) should wrap in $and list."""
        q = And(True, False).query
        assert q == {"$and": [True, False]}

    def test_or_with_dict_expression_unchanged(self):
        """Or with dict expression should still work as before."""
        q = Or({"x": 1}).query
        assert q == {"x": 1}

    def test_or_with_multiple_dict_expressions_unchanged(self):
        """Or with multiple dict expressions should still work as before."""
        q = Or({"x": 1}, {"y": 2}).query
        assert q == {"$or": [{"x": 1}, {"y": 2}]}

    def test_and_with_dict_expression_unchanged(self):
        """And with dict expression should still work as before."""
        q = And({"x": 1}).query
        assert q == {"x": 1}

    def test_nor_with_bool(self):
        """Nor(True) should return proper dict."""
        q = Nor(True).query
        assert q == {"$nor": [True]}

    def test_nor_with_dict_unchanged(self):
        """Nor with dict expression should still work."""
        q = Nor({"x": 1}).query
        assert q == {"$nor": [{"x": 1}]}

    def test_or_empty_query_raises(self):
        """Or() with no expressions should raise AttributeError on .query access."""
        op = Or()
        with pytest.raises(AttributeError, match="At least one expression"):
            _ = op.query

    def test_and_empty_query_raises(self):
        """And() with no expressions should raise AttributeError on .query access."""
        op = And()
        with pytest.raises(AttributeError, match="At least one expression"):
            _ = op.query
