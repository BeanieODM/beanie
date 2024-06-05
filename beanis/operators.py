from beanis.odm.operators.find.array import All, ElemMatch, Size
from beanis.odm.operators.find.bitwise import (
    BitsAllClear,
    BitsAllSet,
    BitsAnyClear,
    BitsAnySet,
)
from beanis.odm.operators.find.comparison import (
    GT,
    GTE,
    LT,
    LTE,
    NE,
    Eq,
    In,
    NotIn,
)
from beanis.odm.operators.find.element import Exists, Type
from beanis.odm.operators.find.evaluation import (
    Expr,
    JsonSchema,
    Mod,
    RegEx,
    Text,
    Where,
)
from beanis.odm.operators.find.geospatial import (
    Box,
    GeoIntersects,
    GeoWithin,
    GeoWithinTypes,
    Near,
    NearSphere,
)
from beanis.odm.operators.find.logical import And, Nor, Not, Or
from beanis.odm.operators.update.array import (
    AddToSet,
    Pop,
    Pull,
    PullAll,
    Push,
)
from beanis.odm.operators.update.bitwise import Bit
from beanis.odm.operators.update.general import (
    CurrentDate,
    Inc,
    Max,
    Min,
    Mul,
    Rename,
    Set,
    SetOnInsert,
    Unset,
)

__all__ = [
    # Find
    # Array
    "All",
    "ElemMatch",
    "Size",
    # Bitwise
    "BitsAllClear",
    "BitsAllSet",
    "BitsAnyClear",
    "BitsAnySet",
    # Comparison
    "Eq",
    "GT",
    "GTE",
    "In",
    "NotIn",
    "LT",
    "LTE",
    "NE",
    # Element
    "Exists",
    "Type",
    "Type",
    # Evaluation
    "Expr",
    "JsonSchema",
    "Mod",
    "RegEx",
    "Text",
    "Where",
    # Geospatial
    "GeoIntersects",
    "GeoWithinTypes",
    "GeoWithin",
    "Box",
    "Near",
    "NearSphere",
    # Logical
    "Or",
    "And",
    "Nor",
    "Not",
    # Update
    # Array
    "AddToSet",
    "Pop",
    "Pull",
    "Push",
    "PullAll",
    # Bitwise
    "Bit",
    # General
    "Set",
    "CurrentDate",
    "Inc",
    "Min",
    "Max",
    "Mul",
    "Rename",
    "SetOnInsert",
    "Unset",
]
