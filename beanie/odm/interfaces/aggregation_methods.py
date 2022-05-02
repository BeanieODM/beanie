from abc import abstractmethod
from typing import Any, Optional, Union, List, Dict, cast

from pymongo.client_session import ClientSession

from beanie.odm.fields import ExpressionField


class AggregateMethods:
    """
    Aggregate methods
    """

    @abstractmethod
    def aggregate(
        self,
        aggregation_pipeline,
        projection_model=None,
        session=None,
        ignore_cache: bool = False,
    ):
        ...

    async def sum(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        """
        Sum of values of the given field

        Example:

        ```python

        class Sample(Document):
            price: int
            count: int

        sum_count = await Document.find(Sample.price <= 100).sum(Sample.count)

        ```

        :param field: Union[str, ExpressionField]
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool
        :return: float - sum. None if there are no items.
        """
        pipeline = [
            {"$group": {"_id": None, "sum": {"$sum": f"${field}"}}},
            {"$project": {"_id": 0, "sum": 1}},
        ]

        # As we did not supply a projection we can safely cast the type (hinting to mypy that we know the type)
        result: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            await self.aggregate(
                aggregation_pipeline=pipeline,
                session=session,
                ignore_cache=ignore_cache,
            ).to_list(),  # type: ignore # TODO: pyright issue, fix
        )
        if not result:
            return None
        return result[0]["sum"]

    async def avg(
        self,
        field,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        """
        Average of values of the given field

        Example:

        ```python

        class Sample(Document):
            price: int
            count: int

        avg_count = await Document.find(Sample.price <= 100).avg(Sample.count)
        ```

        :param field: Union[str, ExpressionField]
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool
        :return: Optional[float] - avg. None if there are no items.
        """
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": f"${field}"}}},
            {"$project": {"_id": 0, "avg": 1}},
        ]

        result: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            await self.aggregate(
                aggregation_pipeline=pipeline,
                session=session,
                ignore_cache=ignore_cache,
            ).to_list(),  # type: ignore # TODO: pyright issue, fix
        )
        if not result:
            return None
        return result[0]["avg"]

    async def max(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        """
        Max of the values of the given field

        Example:

        ```python

        class Sample(Document):
            price: int
            count: int

        max_count = await Document.find(Sample.price <= 100).max(Sample.count)
        ```

        :param field: Union[str, ExpressionField]
        :param session: Optional[ClientSession] - pymongo session
        :return: float - max. None if there are no items.
        """
        pipeline = [
            {"$group": {"_id": None, "max": {"$max": f"${field}"}}},
            {"$project": {"_id": 0, "max": 1}},
        ]

        result: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            await self.aggregate(
                aggregation_pipeline=pipeline,
                session=session,
                ignore_cache=ignore_cache,
            ).to_list(),  # type: ignore # TODO: pyright issue, fix
        )
        if not result:
            return None
        return result[0]["max"]

    async def min(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Optional[float]:
        """
        Min of the values of the given field

        Example:

        ```python

        class Sample(Document):
            price: int
            count: int

        min_count = await Document.find(Sample.price <= 100).min(Sample.count)
        ```

        :param field: Union[str, ExpressionField]
        :param session: Optional[ClientSession] - pymongo session
        :return: float - min. None if there are no items.
        """
        pipeline = [
            {"$group": {"_id": None, "min": {"$min": f"${field}"}}},
            {"$project": {"_id": 0, "min": 1}},
        ]

        result: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            await self.aggregate(
                aggregation_pipeline=pipeline,
                session=session,
                ignore_cache=ignore_cache,
            ).to_list(),  # type: ignore # TODO: pyright issue, fix
        )
        if not result:
            return None
        return result[0]["min"]
