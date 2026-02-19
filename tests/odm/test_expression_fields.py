from beanie.odm.enums import SortDirection
from beanie.odm.fields import ExpressionField, FieldResolution
from beanie.odm.operators.find.comparison import In, NotIn
from beanie.odm.utils.relations import resolve_query_paths
from tests.odm.models import (
    DocumentWithDeepNestedAlias,
    DocumentWithNestedAlias,
    Door,
    House,
    Sample,
    Window,
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


class TestFieldResolution:
    """Tests for FieldResolution metadata on ExpressionField."""

    def test_non_link_field_has_no_link_flag(self):
        """Embedded model fields are not marked as links."""
        expr = Sample.nested
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is False

    def test_link_field_has_link_flag(self):
        """Direct Link fields carry is_link=True."""
        expr = House.door
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is True

    def test_list_link_field_has_link_flag(self):
        """List[Link[...]] fields carry is_link=True."""
        expr = House.windows
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is True

    def test_optional_link_field_has_link_flag(self):
        """Optional[Link[...]] fields carry is_link=True."""
        expr = House.roof
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is True

    def test_link_subfield_propagates_flag(self):
        """Accessing a sub-field through a link propagates is_link."""
        expr = House.door.id
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is True

    def test_non_link_subfield_no_flag(self):
        """Sub-fields of embedded models don't get is_link."""
        expr = Sample.nested.integer
        assert isinstance(expr, ExpressionField)
        assert expr._field_resolution.is_link is False

    def test_link_model_class_resolved(self):
        """Link fields resolve the linked model class."""
        expr = House.door
        assert expr._field_resolution.model_class is Door

    def test_nested_link_model_class_resolved(self):
        """Deep navigation through links resolves chained model classes."""
        # Door.window is Optional[Link[Window]]
        expr = House.door.window
        assert expr._field_resolution.model_class is Window
        assert expr._field_resolution.is_link is True

    def test_link_alias_resolution(self):
        """Alias resolution works through Link model fields."""
        # Door.t has no alias, so it stays as "t"
        expr = House.door.t
        assert expr == "door.t"
        assert expr._field_resolution.is_link is True

    def test_link_id_alias_resolution(self):
        """The 'id' field resolves to alias '_id' through links."""
        expr = House.door.id
        assert expr == "door._id"
        assert expr._field_resolution.is_link is True

    def test_embedded_model_no_link_flag(self):
        """Embedded BaseModel fields are not links."""
        resolution = ExpressionField._resolve_field(
            DocumentWithNestedAlias.model_fields["nested_field"].annotation
        )
        assert resolution.is_link is False
        assert resolution.model_class is not None

    def test_resolve_field_plain_type(self):
        """Primitive types produce empty resolution."""
        resolution = ExpressionField._resolve_field(int)
        assert resolution.model_class is None
        assert resolution.is_link is False

    def test_resolve_field_none(self):
        """None annotation produces empty resolution."""
        resolution = ExpressionField._resolve_field(None)
        assert resolution == FieldResolution()

    def test_getitem_propagates_link_flag(self):
        """__getitem__ access also propagates the is_link flag."""
        expr = House.door["t"]
        assert expr == "door.t"
        assert expr._field_resolution.is_link is True


class TestResolveQueryPaths:
    """Tests for resolve_query_paths — DBRef translation at query time."""

    def test_link_id_without_fetch(self):
        """Without fetch_links, door._id becomes door.$id."""
        raw = {House.door.id: "some_id"}
        resolved = resolve_query_paths(raw, House, fetch_links=False)
        assert resolved == {"door.$id": "some_id"}

    def test_link_id_with_fetch(self):
        """With fetch_links, door._id stays as door._id."""
        raw = {House.door.id: "some_id"}
        resolved = resolve_query_paths(raw, House, fetch_links=True)
        assert resolved == {"door._id": "some_id"}

    def test_non_link_field_unchanged(self):
        """Non-link fields pass through unmodified."""
        raw = {Sample.integer: 42}
        resolved = resolve_query_paths(raw, Sample, fetch_links=False)
        assert resolved == {"integer": 42}

    def test_nested_operator_dict(self):
        """Operator dicts (e.g., $gt) are recursed into."""
        raw = {House.door.id: {"$in": ["a", "b"]}}
        resolved = resolve_query_paths(raw, House, fetch_links=False)
        assert resolved == {"door.$id": {"$in": ["a", "b"]}}

    def test_list_values_recursed(self):
        """Lists containing dicts are recursed into."""
        raw = {"$or": "ignored"}
        # Verify plain string values pass through
        resolved = resolve_query_paths(raw, House, fetch_links=False)
        assert resolved == {"$or": "ignored"}

    def test_plain_string_key_unchanged(self):
        """Plain string keys (not ExpressionField) are never translated."""
        raw = {"door._id": "some_id"}
        resolved = resolve_query_paths(raw, House, fetch_links=False)
        # Plain str is not ExpressionField, so no translation
        assert resolved == {"door._id": "some_id"}

    def test_link_non_id_field_unchanged_without_fetch(self):
        """Non-id link sub-fields don't get $id translation."""
        raw = {House.door.t: 10}
        resolved = resolve_query_paths(raw, House, fetch_links=False)
        assert resolved == {"door.t": 10}

    def test_aggregation_pipeline_without_fetch(self):
        """End-to-end: aggregation pipeline uses $id without fetch_links."""
        q = House.find(House.door.id == "abc123")
        pipeline = q.aggregate(
            [{"$group": {"_id": "$height", "count": {"$sum": 1}}}]
        ).get_aggregation_pipeline()
        assert pipeline[0] == {"$match": {"door.$id": "abc123"}}

    def test_aggregation_pipeline_with_fetch(self):
        """End-to-end: aggregation pipeline uses _id with fetch_links."""
        q = House.find(House.door.id == "abc123", fetch_links=True)
        pipeline = q.aggregate(
            [{"$group": {"_id": "$height", "count": {"$sum": 1}}}]
        ).get_aggregation_pipeline()
        # $lookup stages come first, then $match with _id
        match_stages = [s for s in pipeline if "$match" in s]
        assert {"$match": {"door._id": "abc123"}} in match_stages
