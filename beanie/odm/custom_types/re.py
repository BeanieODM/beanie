import re
from typing import Annotated

import bson
import pydantic


def _to_bson_regex(v):
    return v.try_compile() if isinstance(v, bson.Regex) else v


Pattern = Annotated[
    re.Pattern,
    pydantic.BeforeValidator(
        lambda v: v.try_compile() if isinstance(v, bson.Regex) else v
    ),
]

__all__ = ["Pattern"]
