from typing import Any

from pydantic import Field

from beanie.odm.settings.base import ItemSettings


class ViewSettings(ItemSettings):
    source: str | type
    pipeline: list[dict[str, Any]]

    max_nesting_depths_per_field: dict = Field(default_factory=dict)
    max_nesting_depth: int = 3
