from typing import Optional

from pydantic import ConfigDict, Field

from beanie.odm.fields import IndexModelField
from beanie.odm.settings.base import ItemSettings
from beanie.odm.settings.timeseries import TimeSeriesConfig


class DocumentSettings(ItemSettings):
    use_state_management: bool = False
    state_management_replace_objects: bool = False
    state_management_save_previous: bool = False
    validate_on_save: bool = False
    use_revision: bool = False
    single_root_inheritance: bool = False

    indexes: list[IndexModelField] = Field(default_factory=list)
    merge_indexes: bool = False
    timeseries: Optional[TimeSeriesConfig] = None

    lazy_parsing: bool = False

    keep_nulls: bool = True

    max_nesting_depths_per_field: dict = Field(default_factory=dict)
    max_nesting_depth: int = 3

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
