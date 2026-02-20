import re

import bson
import pydantic
from typing_extensions import Annotated

Pattern = Annotated[
    re.Pattern,
    pydantic.BeforeValidator(
        lambda v: v.try_compile() if isinstance(v, bson.Regex) else v
    ),
]
