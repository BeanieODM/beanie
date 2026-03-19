import re
from typing import Annotated

import bson
import pydantic

Pattern = Annotated[
    re.Pattern,
    pydantic.BeforeValidator(
        lambda v: v.try_compile() if isinstance(v, bson.Regex) else v
    ),
]
