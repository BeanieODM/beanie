from abc import abstractmethod
from typing import Any, Optional, TypeVar, Union, overload

from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel

from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.find import FindMany

DocType = TypeVar("DocType", bound="AggregateInterface")
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)


class AggregateInterface:
    @classmethod
    @abstractmethod
    def find_all(cls) -> FindMany:
        pass

    @overload
    @classmethod
    def aggregate(
        cls: type[DocType],
        aggregation_pipeline: list,
        projection_model: None = None,
        session: Optional[AsyncIOMotorClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> AggregationQuery[dict[str, Any]]: ...

    @overload
    @classmethod
    def aggregate(
        cls: type[DocType],
        aggregation_pipeline: list,
        projection_model: type[DocumentProjectionType],
        session: Optional[AsyncIOMotorClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> AggregationQuery[DocumentProjectionType]: ...

    @classmethod
    def aggregate(
        cls: type[DocType],
        aggregation_pipeline: list,
        projection_model: Optional[type[DocumentProjectionType]] = None,
        session: Optional[AsyncIOMotorClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> Union[
        AggregationQuery[dict[str, Any]],
        AggregationQuery[DocumentProjectionType],
    ]:
        """
        Aggregate over collection.
        Returns [AggregationQuery](query.md#aggregationquery) query object
        :param aggregation_pipeline: list - aggregation pipeline
        :param projection_model: Type[BaseModel]
        :param session: Optional[AsyncIOMotorClientSession]
        :param ignore_cache: bool
        :param **pymongo_kwargs: pymongo native parameters for aggregate operation
        :return: [AggregationQuery](query.md#aggregationquery)
        """
        return cls.find_all().aggregate(
            aggregation_pipeline=aggregation_pipeline,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            **pymongo_kwargs,
        )
