from typing import Callable, Any, Type


def get_class_for_method(f: Callable) -> str:
    return f"{f.__module__}.{f.__qualname__.split('.')[0]}"


def get_class_for_object(o: Any) -> Type:
    return o.__class__
