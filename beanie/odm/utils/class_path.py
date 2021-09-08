from typing import Callable, Any


def get_class_path_for_method(f: Callable) -> str:
    return f"{f.__module__}.{f.__qualname__.split('.')[0]}"


def get_class_path_for_object(o: Any) -> str:
    return f"{o.__module__}.{o.__class__.__name__}"
