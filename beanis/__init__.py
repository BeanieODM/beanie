from beanis.migrations.controllers.free_fall import free_fall_migration
from beanis.migrations.controllers.iterative import iterative_migration
from beanis.odm.actions import (
    After,
    Before,
    Delete,
    Insert,
    Replace,
    Save,
    SaveChanges,
    Update,
    ValidateOnSave,
    after_event,
    before_event,
)
from beanis.odm.custom_types import DecimalAnnotation
from beanis.odm.documents import (
    Document,
    MergeStrategy,
)

from beanis.odm.settings.timeseries import Granularity, TimeSeriesConfig
from beanis.odm.utils.init import init_beanis

__version__ = "0.0.1"
__all__ = [
    # ODM
    "Document",
    "init_beanis",
    "TimeSeriesConfig",
    "Granularity",
    "MergeStrategy",
    # Actions
    "before_event",
    "after_event",
    "Insert",
    "Replace",
    "Save",
    "SaveChanges",
    "ValidateOnSave",
    "Delete",
    "Before",
    "After",
    "Update",
    # Migrations
    "iterative_migration",
    "free_fall_migration",
    # Custom Types
    "DecimalAnnotation",
]
