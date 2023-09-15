import sys

if sys.version_info >= (3, 8):
    from typing import get_args, get_origin
else:
    from typing_extensions import get_args, get_origin

import inspect
from typing import Any, Type


def extract_id_class(annotation) -> Type[Any]:
    if get_origin(annotation) is not None:
        try:
            annotation = next(
                arg for arg in get_args(annotation) if arg is not type(None)
            )
        except StopIteration:
            annotation = None
    if inspect.isclass(annotation):
        return annotation
    raise ValueError("Unknown annotation: {}".format(annotation))
