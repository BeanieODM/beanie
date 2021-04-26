from beanie.odm.query_builder.operators.update.general import (
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
from tests.odm.query_builder.models import A


def test_set():
    q = Set({A.i: 2})
    assert q == {"$set": {"i": 2}}


def test_current_date():
    q = CurrentDate({A.i: 2})
    assert q == {"$currentDate": {"i": 2}}


def test_inc():
    q = Inc({A.i: 2})
    assert q == {"$inc": {"i": 2}}


def test_min():
    q = Min({A.i: 2})
    assert q == {"$min": {"i": 2}}


def test_max():
    q = Max({A.i: 2})
    assert q == {"$max": {"i": 2}}


def test_mul():
    q = Mul({A.i: 2})
    assert q == {"$mul": {"i": 2}}


def test_rename():
    q = Rename({A.i: 2})
    assert q == {"$rename": {"i": 2}}


def test_set_on_insert():
    q = SetOnInsert({A.i: 2})
    assert q == {"$setOnInsert": {"i": 2}}


def test_unset():
    q = Unset({A.i: 2})
    assert q == {"$unset": {"i": 2}}
