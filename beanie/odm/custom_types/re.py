import re
from typing import Annotated

from bson import Regex
from pydantic import BeforeValidator

Pattern = Annotated[
    re.Pattern,
    BeforeValidator(lambda v: v.try_compile() if isinstance(v, Regex) else v),
]

__all__ = ["Pattern"]
