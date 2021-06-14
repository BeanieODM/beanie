from beanie.migrations.controllers.free_fall import free_fall_migration
from beanie.migrations.controllers.iterative import iterative_migration
from beanie.odm.fields import PydanticObjectId, Indexed
from beanie.odm.utils.general import init_beanie
from beanie.odm.documents import Document

__version__ = "1.1.2"
__all__ = [
    # ODM
    "Document",
    "init_beanie",
    "PydanticObjectId",
    "Indexed",
    # Migrations
    "iterative_migration",
    "free_fall_migration",
]
