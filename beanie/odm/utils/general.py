from typing import List, Type, Union, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie.odm.utils.init import Initializer

if TYPE_CHECKING:
    from beanie.odm.documents import DocType
    from beanie.odm.views import View


async def init_beanie(
        database: AsyncIOMotorDatabase = None,
        connection_string: str = None,
        document_models: List[
            Union[Type["DocType"], Type["View"], str]] = None,
        allow_index_dropping: bool = False,
        recreate_views: bool = False,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param connection_string: str - MongoDB connection string
    :param document_models: List[Union[Type[DocType], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default False
    :return: None
    """

    await Initializer(
        database=database,
        connection_string=connection_string,
        document_models=document_models,
        allow_index_dropping=allow_index_dropping,
        recreate_views=recreate_views,
    )
