from abc import abstractmethod
from typing import Type, Any

from pydantic import BaseModel

from beanie.odm.queries.aggregation import AggregationPipeline


class AggregateMethods:
    @abstractmethod
    def aggregate(
        self,
        aggregation_pipeline,
        aggregation_model: Type[BaseModel] = None,
    ) -> AggregationPipeline:
        ...

    async def sum(self, field) -> float:
        pipeline = [
            {"$group": {"_id": None, "sum": {"$sum": f"${field}"}}},
            {"$project": {"_id": 0, "sum": 1}},
        ]

        result = await self.aggregate(aggregation_pipeline=pipeline).to_list()
        return result[0]["sum"]

    async def avg(self, field) -> float:
        pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": f"${field}"}}},
            {"$project": {"_id": 0, "avg": 1}},
        ]

        result = await self.aggregate(aggregation_pipeline=pipeline).to_list()
        return result[0]["avg"]

    async def max(self, field) -> Any:
        pipeline = [
            {"$group": {"_id": None, "max": {"$max": f"${field}"}}},
            {"$project": {"_id": 0, "max": 1}},
        ]

        result = await self.aggregate(aggregation_pipeline=pipeline).to_list()
        return result[0]["max"]

    async def min(self, field) -> Any:
        pipeline = [
            {"$group": {"_id": None, "min": {"$min": f"${field}"}}},
            {"$project": {"_id": 0, "min": 1}},
        ]

        result = await self.aggregate(aggregation_pipeline=pipeline).to_list()
        return result[0]["min"]
