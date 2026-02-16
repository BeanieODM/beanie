from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import In, NotIn
from tests.odm.models import (
    DocumentWithDeepNestedAlias,
    DocumentWithNestedAlias,
    Sample,
)


def test_nesting():
    assert Sample.id == "_id"

    q = Sample.find_many(Sample.integer == 1)
    assert q.get_filter_query() == {"integer": 1}
    assert Sample.integer == "integer"

    q = Sample.find_many(Sample.nested.integer == 1)
    assert q.get_filter_query() == {"nested.integer": 1}
    assert Sample.nested.integer == "nested.integer"

    q = Sample.find_many(Sample.union.s == "test")
    assert q.get_filter_query() == {"union.s": "test"}
    assert Sample.union.s == "union.s"

    q = Sample.find_many(Sample.nested.optional == None)  # noqa
    assert q.get_filter_query() == {"nested.optional": None}
    assert Sample.nested.optional == "nested.optional"

    q = Sample.find_many(Sample.nested.integer == 1).find_many(
        Sample.nested.union.s == "test"
    )
    assert q.get_filter_query() == {
        "$and": [{"nested.integer": 1}, {"nested.union.s": "test"}]
    }


def test_eq():
    q = Sample.find_many(Sample.integer == 1)
    assert q.get_filter_query() == {"integer": 1}


def test_gt():
    q = Sample.find_many(Sample.integer > 1)
    assert q.get_filter_query() == {"integer": {"$gt": 1}}


def test_gte():
    q = Sample.find_many(Sample.integer >= 1)
    assert q.get_filter_query() == {"integer": {"$gte": 1}}


def test_in():
    q = Sample.find_many(In(Sample.integer, [1, 2, 3, 4]))
    assert dict(q.get_filter_query()) == {"integer": {"$in": [1, 2, 3, 4]}}


def test_lt():
    q = Sample.find_many(Sample.integer < 1)
    assert q.get_filter_query() == {"integer": {"$lt": 1}}


def test_lte():
    q = Sample.find_many(Sample.integer <= 1)
    assert q.get_filter_query() == {"integer": {"$lte": 1}}


def test_ne():
    q = Sample.find_many(Sample.integer != 1)
    assert q.get_filter_query() == {"integer": {"$ne": 1}}


def test_nin():
    q = Sample.find_many(NotIn(Sample.integer, [1, 2, 3, 4]))
    assert dict(q.get_filter_query()) == {"integer": {"$nin": [1, 2, 3, 4]}}


def test_pos():
    q = +Sample.integer
    assert q == ("integer", SortDirection.ASCENDING)


def test_neg():
    q = -Sample.integer
    assert q == ("integer", SortDirection.DESCENDING)


class TestAliasResolution:
    """Tests for GitHub issues #937 and #945 - alias resolution in nested
    expression fields."""

    def test_nested_field_alias(self):
        """#937: nested BaseModel fields should use alias in queries."""
        # unit_class has alias="unitClass"
        expr = DocumentWithNestedAlias.nested_field.unit_class
        assert expr == "nested_field.unitClass", (
            f"Expected 'nested_field.unitClass', got '{expr}'"
        )

    def test_nested_field_alias_in_query(self):
        """#937: find query with nested aliased field should use alias."""
        q = DocumentWithNestedAlias.find_many(
            DocumentWithNestedAlias.nested_field.unit_class == "tank"
        )
        assert q.get_filter_query() == {"nested_field.unitClass": "tank"}

    def test_nested_field_multiple_aliases(self):
        """Multiple aliased fields on the same nested model."""
        expr_unit = DocumentWithNestedAlias.nested_field.unit_class
        expr_count = DocumentWithNestedAlias.nested_field.item_count
        assert expr_unit == "nested_field.unitClass"
        assert expr_count == "nested_field.itemCount"

    def test_deep_nested_alias(self):
        """Aliases should resolve at multiple nesting levels."""
        expr = DocumentWithDeepNestedAlias.deep.inner.unit_class
        assert expr == "deep.innerAlias.unitClass", (
            f"Expected 'deep.innerAlias.unitClass', got '{expr}'"
        )

    def test_non_aliased_nested_field_unchanged(self):
        """Fields without aliases should still work normally."""
        assert Sample.nested.integer == "nested.integer"
        assert Sample.nested.option_1.s == "nested.option_1.s"
