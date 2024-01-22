from typing import Any, Dict, List, Type, Union

from pydantic import Field

from beanie.odm.settings.base import ItemSettings


class ViewSettings(ItemSettings):
    source: Union[str, Type]
    pipeline: List[Dict[str, Any]]

    nesting_depths: dict = Field(default_factory=dict)
    max_nesting_depth: int = 3
