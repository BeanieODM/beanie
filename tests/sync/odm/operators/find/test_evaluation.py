from beanie.odm.operators.find.evaluation import (
    Expr,
    JsonSchema,
    Mod,
    RegEx,
    Text,
    Where,
)
from tests.sync.models import Sample


def test_expr():
    q = Expr({"a": "B"})
    assert q == {"$expr": {"a": "B"}}


def test_json_schema():
    q = JsonSchema({"a": "B"})
    assert q == {"$jsonSchema": {"a": "B"}}


def test_mod():
    q = Mod(Sample.integer, 3, 2)
    assert q == {"integer": {"$mod": [3, 2]}}


def test_regex():
    q = RegEx(Sample.integer, "smth")
    assert q == {"integer": {"$regex": "smth"}}

    q = RegEx(Sample.integer, "smth", "options")
    assert q == {"integer": {"$regex": "smth", "$options": "options"}}


def test_text():
    q = Text("something")
    assert q == {
        "$text": {
            "$search": "something",
            "$caseSensitive": False,
            "$diacriticSensitive": False,
        }
    }
    q = Text("something", case_sensitive=True)
    assert q == {
        "$text": {
            "$search": "something",
            "$caseSensitive": True,
            "$diacriticSensitive": False,
        }
    }
    q = Text("something", diacritic_sensitive=True)
    assert q == {
        "$text": {
            "$search": "something",
            "$caseSensitive": False,
            "$diacriticSensitive": True,
        }
    }
    q = Text("something", language="test")
    assert q == {
        "$text": {
            "$search": "something",
            "$caseSensitive": False,
            "$diacriticSensitive": False,
            "$language": "test",
        }
    }


def test_where():
    q = Where("test")
    assert q == {"$where": "test"}
