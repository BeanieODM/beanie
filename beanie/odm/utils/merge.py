from pydantic.main import BaseModel
from beanie.odm.fields import Link


def merge_models(left: BaseModel, right: BaseModel) -> None:
    for k, left_value in left.__iter__():
        if hasattr(right, k):
            right_value = right.__getattribute__(k)
            if isinstance(right_value, BaseModel) and isinstance(
                left_value, BaseModel
            ):
                merge_models(left_value, right_value)
            elif isinstance(right_value, list):
                links_found = False
                for i in right_value:
                    if isinstance(i, Link):
                        links_found = True
                        break
                if links_found:
                    continue
            elif not isinstance(right_value, Link):
                left.__setattr__(k, right_value)
