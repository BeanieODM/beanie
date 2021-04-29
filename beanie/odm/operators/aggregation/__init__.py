from abc import ABC

from beanie.odm.operators import BaseOperator


class BaseAggregationOperator(BaseOperator, ABC):
    ...


class BaseAggregationStage(BaseOperator, ABC):
    ...
