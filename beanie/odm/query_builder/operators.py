from enum import Enum


class Operators(str, Enum):
    # Comparison
    EQ = "EQ"
    GT = "GT"
    GTE = "GTE"
    IN = "IN"
    LT = "LT"
    LTE = "LTE"
    NE = "NE"
    NIN = "NIN"

    # Logical
    AND = "AND"
    NOT = "NOT"
    NOR = "NOR"
    OR = "OR"

    # Element
    EXISTS = "EXISTS"
    TYPE = "TYPE"

    # Evaluation
    EXPR = "EXPR"  # ?
    JSON_SCHEMA = "JSON_SCHEMA"  # ?
    MOD = "MOD"
    REGEX = "REGEX"
    TEXT = "TEXT"
    WHERE = "WHERE"  # ?

    # Geospatial
    GEO_INTERSECTS = "GEO_INTERSECTS"
    GEO_WITHIN = "GEO_WITHIN"
    NEAR = "NEAR"
    NEAR_SPHERE = "NEAR_SPHERE"

    # Array
    ALL = "ALL"
    ELEM_MATCH = "ELEM_MATCH"
    SIZE = "SIZE"

    # Bitwise
    BITS_ALL_CLEAR = "BITS_ALL_CLEAR"
    BITS_ALL_SET = "BITS_ALL_SET"
    BITS_ANY_CLEAR = "BITS_ANY_CLEAR"
    BITS_ANY_SET = "BITS_ANY_SET"

    # Projection Operators
    DOLLAR = "$"  # ?
    PROJECTION_ELEM_MATCH = "PROJECTION_ELEM_MATCH"
    META = "META"
    SLICE = "SLICE"

    # Miscellaneous Operators
    COMMENT = "COMMENT"
    RAND = "RAND"
