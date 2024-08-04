from beanie.odm.operators.update.array import (
    AddToSet,
    AddToSetEach,
    Pull,
    PullAll,
    Pop,
    Push,
    PushEach,
)
from tests.odm.models import Sample


def test_add_to_set():
    q = AddToSet({Sample.integer: 2})
    assert q == {"$addToSet": {"integer": 2}}


def test_add_to_set_each():
    q = AddToSetEach({Sample.integer: [2]})
    assert q == {"$addToSet": {"integer": {"$each": [2]}}}


def test_pop():
    q = Pop({Sample.integer: 2})
    assert q == {"$pop": {"integer": 2}}


def test_pull():
    q = Pull({Sample.integer: 2})
    assert q == {"$pull": {"integer": 2}}


def test_push():
    q = Push({Sample.integer: 2})
    assert q == {"$push": {"integer": 2}}


def test_push_each():
    q = PushEach({Sample.integer: [2]})
    assert q == {'$push': {'integer': {'$each': [2]}}}


def test_pull_all():
    q = PullAll({Sample.integer: 2})
    assert q == {"$pullAll": {"integer": 2}}
