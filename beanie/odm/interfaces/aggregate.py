from abc import abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Union, overload

from pydantic import BaseModel
from pymongo.asynchronous.client_session import AsyncClientSession

from beanie.odm.fields import ExpressionField
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
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: None = None,
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> AggregationQuery[Dict[str, Any]]: ...

    @overload
    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: Type[DocumentProjectionType],
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> AggregationQuery[DocumentProjectionType]: ...

    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs: Any,
    ) -> Union[
        AggregationQuery[Dict[str, Any]],
        AggregationQuery[DocumentProjectionType],
    ]:
        """
        Aggregate over collection.
        Returns [AggregationQuery](query.md#aggregationquery) query object
        :param aggregation_pipeline: list - aggregation pipeline
        :param projection_model: Type[BaseModel]
        :param session: Optional[AsyncClientSession] - pymongo session.
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

    @classmethod
    async def sum(
        cls,
        field: Union[str, ExpressionField],
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        return await cls.find_all().sum(field, session, ignore_cache)

    @classmethod
    async def avg(
        cls,
        field,
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        return await cls.find_all().avg(field, session, ignore_cache)

    @classmethod
    async def max(
        cls,
        field: Union[str, ExpressionField],
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        return await cls.find_all().max(field, session, ignore_cache)

    @classmethod
    async def min(
        cls,
        field: Union[str, ExpressionField],
        session: Optional[AsyncClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        return await cls.find_all().min(field, session, ignore_cache)
