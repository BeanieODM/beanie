from collections import Mapping
from typing import Union

from beanie.odm.query_builder.operators.aggregation import BaseAggregationStage


class CollectionStage(BaseAggregationStage):
    ...


class AddFields(CollectionStage):
    def __init__(self, expression: Union[Mapping, dict]):
        self.expression = expression

    @property
    def query(self):
        return {"$addFields": self.expression}
