from beanie.odm.operators.update.general import (
    Set,
    CurrentDate,
    Inc,
    Unset,
    SetOnInsert,
    Rename,
    Mul,
    Max,
    Min,
)
from tests.odm.models import Sample


def test_set():
    q = Set({Sample.integer: 2})
    assert q == {"$set": {"integer": 2}}


def test_current_date():
    q = CurrentDate({Sample.integer: 2})
    assert q == {"$currentDate": {"integer": 2}}


def test_inc():
    q = Inc({Sample.integer: 2})
    assert q == {"$inc": {"integer": 2}}


def test_min():
    q = Min({Sample.integer: 2})
    assert q == {"$min": {"integer": 2}}


def test_max():
    q = Max({Sample.integer: 2})
    assert q == {"$max": {"integer": 2}}


def test_mul():
    q = Mul({Sample.integer: 2})
    assert q == {"$mul": {"integer": 2}}


def test_rename():
    q = Rename({Sample.integer: 2})
    assert q == {"$rename": {"integer": 2}}


def test_set_on_insert():
    q = SetOnInsert({Sample.integer: 2})
    assert q == {"$setOnInsert": {"integer": 2}}


def test_unset():
    q = Unset({Sample.integer: 2})
    assert q == {"$unset": {"integer": 2}}
