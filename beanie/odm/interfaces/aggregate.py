from abc import abstractmethod
from typing import Type, Any, Optional, Union, List, Dict

from pydantic import BaseModel
from pymongo.client_session import ClientSession

from beanie.odm.fields import ExpressionField
from beanie.odm.queries.aggregation import AggregationQuery


class AggregateMethods:
    """
    Aggregate methods
    """

    @abstractmethod
    def aggregate(
        self,
        aggregation_pipeline,
        projection_model: Type[BaseModel] = None,
        session: Optional[ClientSession] = None,
    ) -> AggregationQuery:
        ...

    async def sum(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
    ) -> float:
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
        :return: float - sum
        """
        pipeline = [
            {"$group": {"_id": None, "sum": {"$sum": f"${field}"}}},
            {"$project": {"_id": 0, "sum": 1}},
        ]

        result: List[Dict[str, Any]] = await self.aggregate(
            aggregation_pipeline=pipeline, session=session
        ).to_list()
        return result[0]["sum"]

    async def avg(
        self, field, session: Optional[ClientSession] = None
    ) -> float:
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
        :return: float - avg
        """
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": f"${field}"}}},
            {"$project": {"_id": 0, "avg": 1}},
        ]

        result: List[Dict[str, Any]] = await self.aggregate(
            aggregation_pipeline=pipeline, session=session
        ).to_list()
        return result[0]["avg"]

    async def max(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
    ) -> Any:
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
        :return: float - max
        """
        pipeline = [
            {"$group": {"_id": None, "max": {"$max": f"${field}"}}},
            {"$project": {"_id": 0, "max": 1}},
        ]

        result: List[Dict[str, Any]] = await self.aggregate(
            aggregation_pipeline=pipeline, session=session
        ).to_list()
        return result[0]["max"]

    async def min(
        self,
        field: Union[str, ExpressionField],
        session: Optional[ClientSession] = None,
    ) -> Any:
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
        :return: float - max
        """
        pipeline = [
            {"$group": {"_id": None, "min": {"$min": f"${field}"}}},
            {"$project": {"_id": 0, "min": 1}},
        ]

        result: List[Dict[str, Any]] = await self.aggregate(
            aggregation_pipeline=pipeline, session=session
        ).to_list()
        return result[0]["min"]
